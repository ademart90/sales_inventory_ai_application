from fastapi import FastAPI, HTTPException, APIRouter
import os 
from dotenv import load_dotenv
import json
import logging
import warnings
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.schemas.reporting_schema import QueryRequest, prompt_text, ChatTurn
from src.pipelines.sales_pipeline import load_clean_sales
from src.pipelines.inventory_pipeline import load_clean_inventory
from fastapi.responses import StreamingResponse
from src.pipelines.chart_pipeline import plot_chart
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
router = APIRouter()
load_dotenv()

api_key =  os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
llm_with_tools = llm.bind_tools([plot_chart])

sales_summary_path = './json_uploads/sales_summary.json'
inventory_summary_path = './json_uploads/inventory_summary.json'



@router.post('/ai_report')
async def report(payload: QueryRequest):
    try:

        sales_data = (
            load_clean_sales(sales_summary_path)
            if os.path.exists(sales_summary_path)
            else 'no sales summary file found'
        )

        inventory_data = (
            load_clean_inventory(inventory_summary_path)
            if os.path.exists(inventory_summary_path)
            else 'no inventory summary file found'
        )

        combined_context = (
            f'sales data \n{sales_data}\n\n'
            f'inventory data \n{inventory_data}'
        )

        prompt_template = PromptTemplate.from_template(prompt_text)
        input_question = payload.query
        prompt = (
            prompt_template.format(query=input_question, json_string=combined_context)
            + "\n\nNote: If the user asks for a chart or graph, use the `plot_chart` tool with exact values from the JSON and include the returned chart URL in your response."
        )



        async def generate_stream():
            messages = []
            for turn in payload.history:
              if turn.role == "user":
                     
                messages.append(HumanMessage(content=turn.content))
              elif turn.role == "assistant":
            
                messages.append(AIMessage(content=turn.content))

            messages.append(HumanMessage(content=prompt))

            generated_charts_b64 = []

            #checks if Gemini wants to call `plot_chart`
            ai_response = await llm_with_tools.ainvoke(messages)

            if ai_response.tool_calls:
                messages.append(ai_response)
                

                for tool_call in ai_response.tool_calls:
                    if tool_call["name"] == "plot_chart":
                        chart_b64 = plot_chart.invoke(tool_call["args"])
                        generated_charts_b64.append(chart_b64)
                        messages.append(
                            ToolMessage(
                                content="Chart generated successfully in memeory. Summarize chart insights without outputting URLs or base64 strings",
                                tool_call_id=tool_call["id"]
                            )
                        )

                async for chunk in llm_with_tools.astream(messages):
                            text = chunk.text
                            if text:
                                yield text
            else:
                # No chart requested: yield the text directly
                if ai_response.text:
                    yield ai_response.text

            for b64_str in generated_charts_b64:
                yield f"\n<<<CHART_START>>>{b64_str}<<<CHART_END>>>"
    

            logging.getLogger('google_genai').setLevel(logging.ERROR)

            warnings.filterwarnings("ignore", message=".*Direct use of automatic function calling.* ")

        return StreamingResponse(generate_stream(), media_type='text/plain')

                
                
    except Exception as e:
                raise HTTPException(status_code=500, detail=f'gemini api error: {str(e)}')




