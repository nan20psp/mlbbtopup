# history.py

import os
from telegram import Update
from telegram.ext import ContextTypes
import database as db

# (ကိုကို့ main.py ထဲက Helper function တွေကို ဒီမှာ ပြန်ဆောက်ရပါမယ်)
def is_owner(user_id):
    """Check if user is the owner (ADMIN_ID)"""
    try:
        ADMIN_ID = int(os.environ.get("ADMIN_ID"))
        return int(user_id) == ADMIN_ID
    except:
        return False

# (main.py (Line 4005) ကနေ ခေါ်မယ့် function)
async def clear_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """(Owner Only) User တစ်ယောက်၏ history (orders/topups) များကို ဖျက်ပါ။"""
    user_id = str(update.effective_user.id)
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ ဤ command ကို Owner (ADMIN_ID) တစ်ဦးတည်းသာ အသုံးပြုနိုင်ပါသည်။")
        return

    args = context.args
    balance_to_set = None # Default က Balance ကို မထိပါ

    if len(args) == 0 or len(args) > 2:
         await update.message.reply_text(
            "❌ Format မှားနေပါပြီ!\n\n"
            "**History ဖျက်ရန်:**\n"
            "`/clearhistory <user_id>`\n\n"
            "**History ဖျက်ပြီး Balance (0) သတ်မှတ်ရန်:**\n"
            "`/clearhistory <user_id> 0`",
            parse_mode="Markdown"
        )
         return

    target_user_id = args[0]
    if len(args) == 2:
        try:
            balance_to_set = int(args[1])
        except ValueError:
            await update.message.reply_text("❌ Balance (ဂဏန်း) မှားနေပါသည်။ ဥပမာ: `0`")
            return

    # User ရှိမရှိ အရင်စစ်
    user_data = db.get_user(target_user_id)
    if not user_data:
        await update.message.reply_text(f"❌ User ID `{target_user_id}` ကို မတွေ့ရှိပါ။")
        return

    # DB function (Response 168) ကို ခေါ်ပါ
    success = db.clear_user_history(target_user_id, balance_to_set) 

    if success:
        if balance_to_set is not None:
            await update.message.reply_text(
                f"✅ **Success!**\n"
                f"User `{target_user_id}` ၏ History အားလုံး ဖျက်ပြီး Balance ကို `{balance_to_set}` MMK သတ်မှတ်လိုက်ပါပြီ။"
            )
        else:
            await update.message.reply_text(
                f"✅ **Success!**\n"
                f"User `{target_user_id}` ၏ Order နှင့် Topup History အားလုံးကို ဖျက်လိုက်ပါပြီ။ (Balance မပြောင်းပါ)"
            )
    else:
        await update.message.reply_text("❌ User ကို ရှာမတွေ့ပါ (သို့) Error ဖြစ်နေပါသည်။")
