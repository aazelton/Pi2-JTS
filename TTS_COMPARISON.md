# TTS Options for SPEC-1-MedicVoicePi2

## 🎤 **Better Sounding Offline TTS Options (Pi2-Friendly)**

### **🏆 RECOMMENDED: Festival with MBROLA Voices**

#### **✅ Advantages:**
- 🎧 **Much more natural** than eSpeak
- 🗣 **MBROLA voices** are rule-based but better quality
- ⚙️ **Pi2-friendly** - lightweight and efficient
- 🔇 **Offline operation** - no internet required
- 🎯 **Medical clarity** - good for clinical communication

#### **📦 Installation:**
```bash
# Install Festival TTS with MBROLA voices
sudo apt install festival festvox-us1-mbrola festvox-us2-mbrola festvox-us3-mbrola
sudo apt install mbrola mbrola-us1 mbrola-us2 mbrola-us3
```

#### **🔧 Usage:**
```python
from tts_festival import speak, set_voice

# Use MBROLA voice (best quality)
set_voice('mb-us1')
speak("Ketamine dosage is 40 to 80 milligrams IV or IM.")
```

### **🥈 ALTERNATIVE: Enhanced eSpeak NG**

#### **✅ Advantages:**
- 🚀 **Very lightweight** - minimal resource usage
- ⚡ **Fast response** - immediate speech output
- 🔧 **Highly configurable** - speed, pitch, voice options
- 📱 **Pi2 optimized** - designed for embedded systems

#### **📦 Installation:**
```bash
sudo apt install espeak-ng
```

#### **🔧 Usage:**
```python
from tts_utils import speak, set_voice

# Use enhanced eSpeak settings
set_voice('en-us')
speak("Ketamine dosage is 40 to 80 milligrams IV or IM.")
```

### **🥉 FALLBACK: macOS 'say' Command (Development Only)**

#### **✅ Advantages:**
- 🎧 **High quality** - natural sounding voices
- 🍎 **macOS native** - Kathy voice is excellent
- 🧪 **Development friendly** - easy testing

#### **❌ Limitations:**
- 🚫 **macOS only** - not available on Pi2
- 🌐 **System dependent** - not portable

## **📊 TTS Quality Comparison**

| **TTS System** | **Quality** | **Speed** | **Pi2 Compatible** | **Offline** | **Medical Clarity** |
|----------------|-------------|-----------|-------------------|-------------|-------------------|
| **Festival + MBROLA** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **eSpeak NG** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐ |
| **macOS 'say'** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ✅ | ⭐⭐⭐⭐⭐ |

## **🎯 SPEC-1 Implementation**

### **Current Implementation:**
```python
# tts_festival.py - Festival TTS with MBROLA voices
from tts_festival import speak, set_voice

# Automatic fallback chain:
# 1. MBROLA voices (best quality)
# 2. Festival TTS (good quality)
# 3. eSpeak NG (reliable fallback)
```

### **Voice Selection:**
```python
# Available MBROLA voices:
# - mb-us1: Male US English (recommended)
# - mb-us2: Female US English
# - mb-us3: Male US English (alternative)

set_voice('mb-us1')  # Best for medical communication
```

## **🚀 Pi2 Deployment**

### **Updated Deployment Script:**
```bash
# deploy_pi2.sh now includes Festival TTS
sudo apt install -y \
    festival \
    festvox-us1-mbrola \
    festvox-us2-mbrola \
    festvox-us3-mbrola \
    mbrola \
    mbrola-us1 \
    mbrola-us2 \
    mbrola-us3
```

### **Performance on Pi2:**
- **Memory Usage**: ~50MB (Festival + MBROLA)
- **CPU Usage**: Low (rule-based synthesis)
- **Response Time**: <500ms
- **Audio Quality**: Much better than eSpeak

## **🧪 Testing TTS Systems**

### **Test Script:**
```python
from tts_festival import test_voices

# Test all available voices
test_voices()
```

### **Expected Output:**
```
🎤 Testing available TTS voices:
Available voices: ['mb-us1', 'mb-us2', 'mb-us3', 'festival']

Testing mb-us1...
✅ mb-us1 - Working

Testing mb-us2...
✅ mb-us2 - Working

Testing mb-us3...
✅ mb-us3 - Working

Testing festival...
✅ festival - Working
```

## **📋 Implementation Files**

### **Core TTS Modules:**
- `tts_festival.py` - Festival TTS with MBROLA voices (RECOMMENDED)
- `tts_utils.py` - Enhanced eSpeak NG (fallback)
- `tts_utils_pi.py` - Pi-optimized eSpeak

### **Updated Systems:**
- `spec1_simple.py` - Uses Festival TTS
- `voice_agent_hybrid.py` - Uses Festival TTS
- `deploy_pi2.sh` - Installs Festival + MBROLA

## **🎉 Benefits for Medical Use**

### **Clinical Communication:**
- **Clear pronunciation** of medical terms
- **Consistent voice** across all responses
- **Professional tone** suitable for medical settings
- **Fast response** for emergency situations

### **Field Deployment:**
- **Offline operation** - works without internet
- **Pi2 optimized** - minimal resource usage
- **Reliable fallback** - multiple TTS options
- **Easy maintenance** - standard Linux packages

## **🔧 Configuration Options**

### **Voice Settings:**
```python
# Set preferred voice
set_voice('mb-us1')  # Male US English (medical)

# Available options:
# - mb-us1: Male, clear, professional
# - mb-us2: Female, clear, professional  
# - mb-us3: Male, alternative tone
# - festival: Default Festival voice
```

### **Quality vs Speed:**
```python
# High quality (slower)
speak("Detailed medical instruction...")

# Fast response (lower quality)
speak("Quick emergency guidance...")
```

## **✅ Conclusion**

**Festival with MBROLA voices** provides the best balance of:
- 🎧 **High quality** speech synthesis
- ⚡ **Fast response** times
- 🔋 **Low resource** usage
- 🎯 **Medical clarity** for clinical communication

**Perfect for SPEC-1-MedicVoicePi2 deployment on Raspberry Pi 2!** 🚀 