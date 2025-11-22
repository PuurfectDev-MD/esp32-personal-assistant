html = """

<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <script>
        setInterval(function() {
            document.getElementById('camImage').src = '/image?t=' + new Date().getTime();
        }, 10000);
    </script>
    
    <style>
        body { 
            font-family: Arial; 
            background: #f0f0f0; 
            margin: 0; 
            padding: 20px; 
        }
        .container { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            max-width: 400px; 
            margin: 0 auto; 
        }
        .btn { 
            padding: 10px 15px; 
            margin: 5px; 
            border: none; 
            border-radius: 5px; 
            color: white; 
            cursor: pointer; 
        }
        .on { 
            background: #4CAF50; 
        }
        .off { 
            background: #f44336; 
        }
        .image-container {
            text-align: center;
            margin-bottom: 20px;
        }
        #camImage { 
            max-width: 100%; 
            border: 2px solid #666; 
            border-radius: 5px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
</head>
<body>
    <div class="image-container">
        <img id="camImage" src="/image" alt="Camera Feed">
    </div>
    
    <div class="container">
        <h2>ESP32 Control Panel</h2>
        <form>
            <p>LED 1: 
                <button name="LED1" value="ON" class="btn on">ON</button>
                <button name="LED1" value="OFF" class="btn off">OFF</button>
            </p>
            <p>LED 2: 
                <button name="LED2" value="ON" class="btn on">ON</button>
                <button name="LED2" value="OFF" class="btn off">OFF</button>
            </p>
        </form>
    </div>
</body>
</html>


"""