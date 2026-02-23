from rlextra import RLE
import json

#region Report Generation from json to pdf
def generate_report(chat_history_json):
    try:
        # Convert the JSON string to a Python dictionary
        chat_history = json.loads(chat_history_json)

        # Create an RLE instance
        rle = RLE()

        # Generate the report using the RLE instance
        report = rle.generate_report(chat_history)

        return report

    except Exception as e:
        print(f"Error in generate_report => {e}")
        return None