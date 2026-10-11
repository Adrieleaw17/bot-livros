import os
import nest_asyncio
from fpdf import FPDF
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def gerar_pdf(titulo_livro: str, conteudo: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=f"Resumo: {titulo_livro}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texto = conteudo.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 7, txt=texto)
    caminho = "resumo.pdf"
    pdf.output(caminho)
    return caminho

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Olá! Envie o nome de qualquer livro para eu gerar o PDF!")

async def responder_livro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_livro = update.message.text
    await update.message.reply_text(f"⏳ Processando '{nome_livro}'...")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(f"Gere um guia completo e estruturado sobre o livro '{nome_livro}'.")
        caminho = gerar_pdf(nome_livro, resposta.text)
        with open(caminho, "rb") as f_pdf:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=f_pdf, filename=f"{nome_livro}.pdf")
    except Exception as e:
        await update.message.reply_text(f"Erro: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_livro))
    print("🤖 Bot rodando...")
    app.run_polling(close_loop=False)
      
