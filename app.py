import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import re  # Import modul 're' untuk regular expression

# Memuat variabel lingkungan
load_dotenv()

# Inisialisasi Flask dan CORS
app = Flask(__name__)
CORS(app)

# Inisialisasi Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.route('/api/llm-move', methods=['POST'])
def get_llm_move():
    data = request.json
    user_move = data.get('move')
    board = data.get('board')

    print(f"Backend menerima gerakan pengguna: {user_move}") # LOG Backend 1: Gerakan pengguna diterima
    print(f"Backend menerima kondisi papan: {board}") # LOG Backend 2: Kondisi papan diterima

    # Validasi bahwa board memiliki ukuran yang benar
    if len(board) != 6 or any(len(row) != 7 for row in board):
        return jsonify({"error": "Invalid board size"}), 400

    prompt = f"""
    You are an arrogant and conceited Connect 4 player. You constantly belittle your opponent (the User) and are confident of your victory.

    Your opponent just played move: {user_move}. You are playing as LLM. The User's tokens are represented by 🔴, and your tokens are represented by 🟡.

    Here's the current board:

    {board}

    Answer each turn in the following format ONLY:

    Line 1: [Column Number (0-6)]
    Line 2: [A UNIQUE, arrogant, and dismissive explanation of why you chose that column (maximum 20 words). 
    **Do NOT repeat phrases from previous responses**. Avoid starting with the same words multiple times. 
    Use sarcasm, insults, and mockery with more variety.]

    Example Responses:
    3
    Oh, how cute! You really think that was a smart move? This is why I always win.
    
    2
    A toddler could have seen that coming. Try again, but this time, use your brain.
    
    5
    Ah, a desperate move. I’ll enjoy crushing your hopes in a few turns.

    1
    That was adorable. But strategy isn’t your strong suit, is it?

    AGAIN, ONLY the column number on line 1 and the explanation on line 2. NO other text!
    """



    print(f"Prompt yang dikirim ke LLM: {prompt}") # LOG Backend 3: Prompt ke LLM

    # Mengirim prompt ke model LLM
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="llama-3.1-8b-instant"
        )

        llm_response = chat_completion.choices[0].message.content.strip()
        print(f"Respon mentah dari LLM: {llm_response}") # LOG Backend 4: Respon LLM mentah

        # Menggunakan regular expression untuk mengekstrak kolom dan penjelasan
        match = re.search(r"(?s)(?:<think>.*?</think>\s*)?(\d)\s*(.*?)(?=\n|$)", llm_response)

        if match:
            llm_move = match.group(1)
            llm_explanation = match.group(2).strip()

            # Validasi bahwa llm_move adalah angka antara 0 dan 6
            if not llm_move.isdigit() or not 0 <= int(llm_move) <= 6:
                llm_move = "Error"
                llm_explanation = "Invalid column number."
        else:
            llm_move = "Error"
            llm_explanation = "Invalid response format."

        print(f"Gerakan LLM yang diekstrak: {llm_move}") # LOG Backend 5: Gerakan LLM diekstrak
        print(f"Penjelasan LLM yang diekstrak: {llm_explanation}") # LOG Backend 6: Penjelasan LLM diekstrak

        # Mengirimkan respons ke frontend
        return jsonify({"move": llm_move, "explanation": llm_explanation})

    except Exception as e:
        print(f"Error saat memanggil LLM: {e}") # LOG Backend 7: Error LLM
        return jsonify({"move": "Error", "explanation": "Error communicating with LLM."}), 500

# Menjalankan server Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)