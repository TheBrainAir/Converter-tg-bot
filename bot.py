import os
import requests
import json
import base64
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

API_KEY = "CONVERTIO_API_KEY"
TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Convertio Bot! Send me a file to convert it to another format.\n\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot can convert files using Convertio API.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/formats - Show available output formats\n\n"
        "How to use:\n"
        "1. Send a file\n"
        "2. Select the output format\n"
        "3. Wait for the conversion to complete\n"
        "4. Download your converted file"
    )

async def formats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Common formats:\n"
        "Documents: PDF, DOCX, DOC, ODT, RTF, TXT\n"
        "Images: JPG, PNG, GIF, BMP, TIFF, SVG\n"
        "Audio: MP3, WAV, OGG, FLAC, AAC\n"
        "Video: MP4, AVI, MOV, MKV, WEBM\n"
        "Archives: ZIP, RAR, 7Z, TAR\n\n"
        "For a complete list, visit: https://convertio.co/formats/"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    context.user_data["file_name"] = file.file_name
    context.user_data["file_id"] = file.file_id
    
    common_formats = ["pdf", "docx", "jpg", "png", "mp3", "mp4", "txt", "xlsx"]
    
    keyboard = []
    row = []
    for i, fmt in enumerate(common_formats):
        row.append(InlineKeyboardButton(fmt.upper(), callback_data=f"format_{fmt}"))
        if (i + 1) % 4 == 0 or i == len(common_formats) - 1:
            keyboard.append(row)
            row = []
    
    keyboard.append([InlineKeyboardButton("Other format (type manually)", callback_data="format_other")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"I received your file: {file.file_name}\n"
        "Now, select the output format:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("format_"):
        format_choice = data[7:]
        
        if format_choice == "other":
            await query.message.reply_text("Please enter the output format (e.g., pdf, docx, jpg):")
            context.user_data["waiting_for_format"] = True
            return
        
        await query.message.reply_text(f"Converting to {format_choice.upper()}...")
        await convert_file(query.message, context, format_choice)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_format"):
        output_format = update.message.text.lower().strip()
        context.user_data["waiting_for_format"] = False
        
        await update.message.reply_text(f"Converting to {output_format.upper()}...")
        await convert_file(update.message, context, output_format)
    else:
        await update.message.reply_text("Please send me a file to convert or use /help to see available commands.")

async def convert_file(message, context, output_format):
    file_id = context.user_data.get("file_id")
    file_name = context.user_data.get("file_name")
    
    if not file_id or not file_name:
        await message.reply_text("Please send a file first.")
        return
    
    status_message = await message.reply_text("Downloading file...")
    
    try:
        file = await context.bot.get_file(file_id)
        file_content = await file.download_as_bytearray()
        
        await status_message.edit_text("Starting conversion...")
        
        conversion_id = await start_conversion(file_content, file_name, output_format)
        if not conversion_id:
            await status_message.edit_text("Failed to start conversion. Please try again.")
            return
        
        await status_message.edit_text("Converting... Please wait.")
        
        converted_file = await check_conversion_status(conversion_id)
        if not converted_file:
            await status_message.edit_text("Conversion failed. Please try again.")
            return
        
        await status_message.edit_text("Conversion completed. Downloading result...")
        
        result_file = await get_conversion_result(conversion_id)
        if not result_file:
            await status_message.edit_text("Failed to download converted file. Please try again.")
            return
        
        new_file_name = f"{os.path.splitext(file_name)[0]}.{output_format}"
        
        await status_message.edit_text("Sending file...")
        
        await message.reply_document(
            document=result_file,
            filename=new_file_name
        )
        
        await status_message.edit_text("Conversion completed successfully!")
        
    except Exception as e:
        await status_message.edit_text(f"An error occurred: {str(e)}")

async def start_conversion(file_content, file_name, output_format):
    try:
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "apikey": API_KEY,
            "input": "base64",
            "file": encoded_content,
            "filename": file_name,
            "outputformat": output_format
        }
        
        response = requests.post(
            "https://api.convertio.co/convert",
            json=payload
        )
        
        data = response.json()
        
        if data["status"] == "ok":
            return data["data"]["id"]
        else:
            return None
    except Exception:
        return None

async def check_conversion_status(conversion_id):
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(
                f"https://api.convertio.co/convert/{conversion_id}/status"
            )
            
            data = response.json()
            
            if data["status"] == "ok":
                step = data["data"]["step"]
                
                if step == "finish":
                    return data["data"]["output"]["url"]
                elif step == "failed":
                    return None
            
            attempt += 1
            time.sleep(2)
        except Exception:
            attempt += 1
            time.sleep(2)
    
    return None

async def get_conversion_result(conversion_id):
    try:
        response = requests.get(
            f"https://api.convertio.co/convert/{conversion_id}/dl"
        )
        
        data = response.json()
        
        if data["status"] == "ok":
            file_content_base64 = data["data"]["content"]
            return base64.b64decode(file_content_base64)
        else:
            response = requests.get(
                f"https://api.convertio.co/convert/{conversion_id}/status"
            )
            
            status_data = response.json()
            
            if status_data["status"] == "ok" and "output" in status_data["data"] and "url" in status_data["data"]["output"]:
                url = status_data["data"]["output"]["url"]
                file_response = requests.get(url)
                return file_response.content
            
            return None
    except Exception:
        return None

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("formats", formats_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    app.run_polling()

if __name__ == "__main__":
    main()