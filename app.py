from flask import Flask, request, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)

def get_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error: Could not fetch transcript. Reason: {str(e)}"

def summarize_text(text):
    try:
        summarizer = pipeline("summarization", model="t5-small", device=-1)
        words = text.split()
        max_words = 500
        chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=50, min_length=20, do_sample=False)[0]['summary_text']
            # Ensure the summary is a complete sentence and concise
            if not summary.endswith('.'):
                summary += '.'
            summaries.append(summary)
        # Filter out redundant or overly short summaries
        summaries = [s for s in summaries if len(s.split()) > 5]
        # Limit to 5 bullet points max for brevity
        return summaries[:5]
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form["video_url"]
        video_id = get_video_id(video_url)
        if video_id:
            transcript = get_transcript(video_id)
            if "Error" not in transcript:
                summary = summarize_text(transcript)
                if isinstance(summary, str) and "Error" in summary:
                    return render_template("index.html", error=summary)
                return render_template("index.html", summary=summary, video_url=video_url)
            return render_template("index.html", error=transcript)
        return render_template("index.html", error="Invalid YouTube URL")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)