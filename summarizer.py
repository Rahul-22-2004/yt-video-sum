from youtube_transcript_api import YouTubeTranscriptApi
import requests

def get_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        return f"Error: Could not fetch transcript. Reason: {str(e)}"

def summarize_text(text):
    try:
        api_key = "xai-CLRRJXeJn7XZiMqNPTe5kO46Q3gcj1T6xlTSqbq5DwuXsO3mUYfuZux1SPko6mQ3hfmsTk81lli44E8D"  # Replace with your API key
        url = "https://api.x.ai/v1/completions"  # Check exact endpoint in xAI docs
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = f"Summarize the following text in 5 concise bullet points, each a complete sentence under 20 words:\n\n{text}"
        data = {
            "model": "grok-3",
            "prompt": prompt,
            "max_tokens": 200
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            summary_text = response.json()['choices'][0]['text'].strip()
            # Split the summary into bullet points
            points = [point.strip() for point in summary_text.split('\n') if point.strip().startswith('-')]
            # Clean up bullet points (remove leading "- " and ensure they end with a period)
            points = [point[2:].strip() + ('.' if not point.endswith('.') else '') for point in points]
            return points[:5]  # Limit to 5 points
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# Main program
if __name__ == "__main__":
    url = input("Enter YouTube video URL: ")
    video_id = get_video_id(url)
    if video_id:
        transcript = get_transcript(video_id)
        if "Error" not in transcript:
            print("Transcript (first 500 characters):")
            print(transcript[:500])
            print("\nGenerating summary... (this may take a moment)")
            summary = summarize_text(transcript)
            if isinstance(summary, str) and "Error" in summary:
                print(summary)
            else:
                print("\nSummary:")
                for point in summary:
                    print(f"- {point}")
        else:
            print(transcript)
    else:
        print("Invalid YouTube URL. Please use a format like https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID")