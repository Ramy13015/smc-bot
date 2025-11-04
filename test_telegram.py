"""
Test Telegram notification
"""
from app.config import Config
from app.notifier import send_telegram_message

def test_telegram():
    """Test Telegram configuration"""
    print("🔍 Testing Telegram configuration...")
    print(f"Token configured: {bool(Config.TELEGRAM_TOKEN)}")
    print(f"Chat ID configured: {bool(Config.TELEGRAM_CHAT_ID)}")
    
    if not Config.TELEGRAM_TOKEN or not Config.TELEGRAM_CHAT_ID:
        print("❌ Telegram not configured!")
        return False
    
    # Send test message
    message = """
🤖 **SMC Trading Bot - Test Message**

✅ Le bot est opérationnel !
📊 Confluence threshold: 80%
🎯 Prêt à recevoir les signaux TradingView

_Test envoyé le 4 Nov 2025_
    """
    
    print("\n📤 Sending test message to Telegram...")
    success = send_telegram_message(
        message=message,
        token=Config.TELEGRAM_TOKEN,
        chat_id=Config.TELEGRAM_CHAT_ID
    )
    
    if success:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send test message")
    
    return success

if __name__ == "__main__":
    test_telegram()
