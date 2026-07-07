from semantic_kernel import Kernel

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from config.settings import OPENAI_API_KEY, MODEL_NAME

from plugins.customer_plugin import CustomerPlugin

kernel = Kernel()

kernel.add_service(
    OpenAIChatCompletion(
        service_id="chat",
        api_key=OPENAI_API_KEY,
        ai_model_id=MODEL_NAME
    )
)

kernel.add_plugin(
    CustomerPlugin(),
    plugin_name="CustomerPlugin"
)