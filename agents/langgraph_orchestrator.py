import json
import logging

from classification_agent import ClassificationAgent
from extraction_agent import ExtractionAgent
from port_lookup_agent import PortLookupAgent
from container_standardization_agent import ContainerStandardizationAgent
from country_extractor_agent import CountryExtractorAgent
from clarification_agent import ClarificationAgent
from rate_recommendation_agent import RateRecommendationAgent
from response_generator_agent import ResponseGeneratorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

def run_workflow(email_text: str, subject: str, sender: str = "customer@example.com"):
    logger.info("📥 Running workflow...")
    input_data = {"email_text": email_text, "subject": subject, "from": sender}

    # Step 1: Classification
    classification_result = ClassificationAgent().run(input_data)
    logger.info(f"🧠 Classification:\n{json.dumps(classification_result, indent=2)}")

    # Step 2: Extraction
    extraction_result = ExtractionAgent().run(input_data)
    logger.info(f"🔍 Extraction:\n{json.dumps(extraction_result, indent=2)}")

    # Step 3: Port Lookup
    ports = {}
    port_agent = PortLookupAgent()
    for loc in ["origin", "destination"]:
        if extraction_result.get(loc):
            ports[f"{loc}_port"] = port_agent.run({"port_name": extraction_result[loc]})
            logger.info(f"🚢 {loc.capitalize()} Port:\n{json.dumps(ports[f'{loc}_port'], indent=2)}")

    # Step 4: Container Standardization
    container_result = ContainerStandardizationAgent().run({
        "container_type": extraction_result.get("container_type", "")
    })
    logger.info(f"📦 Container:\n{json.dumps(container_result, indent=2)}")

    # Step 5: Country Extraction
    countries = {}
    country_agent = CountryExtractorAgent()
    for loc in ["origin", "destination"]:
        port_data = ports.get(f"{loc}_port", {})
        if port_data.get("port_code"):
            countries[f"{loc}_country"] = country_agent.run({"port_code": port_data["port_code"]})
            logger.info(f"🌍 {loc.capitalize()} Country:\n{json.dumps(countries[f'{loc}_country'], indent=2)}")

    # Step 6: Enrich Extraction
    enriched_extraction = extraction_result.copy()
    enriched_extraction["origin_port_code"] = ports.get("origin_port", {}).get("port_code")
    enriched_extraction["destination_port_code"] = ports.get("destination_port", {}).get("port_code")
    enriched_extraction["standardized_container_type"] = container_result.get("standardized_container_type")
    enriched_extraction["origin_country"] = countries.get("origin_country", {}).get("country")
    enriched_extraction["destination_country"] = countries.get("destination_country", {}).get("country")
    logger.info(f"🔧 Enriched Extraction:\n{json.dumps(enriched_extraction, indent=2)}")

    # Step 7: Clarification (skip validation)
    clarification_input = {
        "extraction_data": enriched_extraction,
        "validation": {"status": "skipped", "missing_fields": []},
        "missing_fields": [],
        "thread_id": f"thread-{hash(email_text) % 10000}"
    }
    clarification_result = ClarificationAgent().run(clarification_input)
    logger.info(f"❓ Clarification:\n{json.dumps(clarification_result, indent=2)}")

    # Step 8: Rate Recommendation
    rate_input = {
        "Origin_Code": enriched_extraction.get("origin_port_code"),
        "Destination_Code": enriched_extraction.get("destination_port_code"),
        "Container_Type": enriched_extraction.get("standardized_container_type") or enriched_extraction.get("container_type", "40DC")
    }
    rate_result = RateRecommendationAgent().run(rate_input)
    logger.info(f"💰 Rate:\n{json.dumps(rate_result, indent=2)}")

    # Step 9: Response Generation
    logger.info("📧 Step 9: Response Generation")

    response_input = {
        "recipient_type": "customer",
        "context": {
            "classification": classification_result,
            "extraction": enriched_extraction,
            "clarification": clarification_result,
            "rate": rate_result
        },
        "previous_messages": [email_text],
        "custom_instructions": "Be polite, mention rate, and thank the customer.",
        "indicative_rate": rate_result.get("indicative_rate")
    }

    response_agent = ResponseGeneratorAgent()
    response_agent.load_context()

    try:
        response_result = response_agent.run(response_input)
        logger.info("📧 Final Response Output:")
        logger.info(json.dumps(response_result, indent=2))
    except Exception as e:
        logger.error(f"❌ Response generation failed: {e}")
        response_result = {"error": str(e), "status": "error"}

    return response_result


# Run sample
run_workflow(
    email_text="We want to ship from jebel ali to mundra,using 20DC containers. The total quantity is 99, total weight is 26 Metric Ton, shipment type is FCL, and the shipment date is 20th June 2025. The cargo is electronics.",
    subject="rate request",
    sender="customer@example.com"
)

