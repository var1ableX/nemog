import logging
from src.app.stubs import user_prompt
from src.services.writer_svc import WriterSvc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """
    Standard entry point which invokes the graph via a call to a service layer.
    """
    # Get input from stub
    input_text = user_prompt()
    print(f"Input received: {input_text}")
    
    # Initialize service
    svc = WriterSvc()
    
    # Run service
    result_message = svc.run(input_text)
    
    # Display result
    print(f"Result: {result_message}")

if __name__ == "__main__":
    main()
