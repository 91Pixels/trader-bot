from PIL import Image

# Convert PNG to ICO
img = Image.open('assets/Cripto-Bot.png')
img.save('assets/Cripto-Bot.ico', format='ICO', sizes=[(256, 256)])
print("✅ Icon created: assets/Cripto-Bot.ico")
