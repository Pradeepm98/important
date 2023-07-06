import java.net.Socket
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStream
import java.io.BufferedWriter
import java.io.OutputStreamWriter


fun main() {
    val serverIp = "13.127.87.242"
    val serverPort = 3000

    val clientSocket = Socket(serverIp, serverPort)


    while (true) {  
    handleRequest(clientSocket)
    }
    // clientSocket.close()
}

fun handleRequest(clientSocket: Socket) {
    println("Connected to server")

    val data = BufferedReader(InputStreamReader(clientSocket.getInputStream()))
    val requestData = data.readLine().toByteArray(Charsets.UTF_8)
    println("Request: ${String(requestData, Charsets.UTF_8)}")
    val dataStr = String(requestData, Charsets.UTF_8)

    val firstLine = dataStr.split('\n')[0]
    val url = firstLine.split(' ')[1]

    println("URL: $url")

    val httpPos = url.indexOf("://")
    val temp = if (httpPos == -1) url else url.substring(httpPos + 3)

    val portPos = temp.indexOf(":")
    var webServerPos = temp.indexOf("/")
    if (webServerPos == -1) {
        webServerPos = temp.length
    }

    val webServer = if (portPos == -1 || webServerPos < portPos) {
        temp.substring(0, webServerPos)
    } else {
        temp.substring(0, portPos)
    }

    val port = if (portPos == -1 || webServerPos < portPos) {
        80
    } else {
        temp.substring(portPos + 1, webServerPos).toInt()
    }

    println("Web Server: $webServer")
    println("Port: $port")
    // val hoste = "jsonip.com"
    // val porte = 80

    // Establish a socket connection to the server

    val serverSocket = Socket(webServer, port)
   // val serverSocket = Socket(webServer, port)
    println("Connected to web server")
    println(serverSocket)
  

    val request = "GET / HTTP/1.1\r\n" +
            "Host: $webServer\r\n" +
            "Connection: close\r\n" +
            "\r\n"

    val writer = BufferedWriter(OutputStreamWriter(serverSocket.getOutputStream()))
    //print type of request
    println("Request: $request")
    writer.write(request)
    writer.flush()

    println("Request sent to web server")
    
    // serverOutputStream.write(requestData)
    // serverOutputStream.flush()

    val reply = serverSocket.getInputStream().readBytes()
    clientSocket.getOutputStream().write(reply)
    clientSocket.getOutputStream().flush()
    // print reply
    println("Reply: ${String(reply, Charsets.UTF_8)}")



    val reader = BufferedReader(InputStreamReader(serverSocket.getInputStream()))
    var line: String?
    while (reader.readLine().also { line = it } != null) {
        println(line)
    }

    //serverSocket.close()
}
