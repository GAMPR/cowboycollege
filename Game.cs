using UnityEngine;
using System.Net.Sockets;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using UnityEngine.UI;
using System;

public class GetVideoScript2 : MonoBehaviour
{
    public RawImage videoDisplay;
    private TcpClient client;
    private NetworkStream stream;
    private Texture2D texture;
    private byte[] sizeBuffer = new byte[4];

    void Start()
    {
        client = new TcpClient("127.0.0.1", 9999);
        stream = client.GetStream();
        texture = new Texture2D(2, 2);  // Placeholder size
        Debug.Log("Bada bing bada boom. Connected to Python server.");
    }

    void Update()
    {
        try
        {
            if (stream.DataAvailable)
            {
                // Read the frame size
                int bytesRead = stream.Read(sizeBuffer, 0, sizeBuffer.Length);
                if (bytesRead < 4)
                {
                    Debug.LogWarning("Did not read a full 4-byte size. Skipping this frame.");
                    return;
                }

                // Reverse byte order if necessary
                if (BitConverter.IsLittleEndian)
                {
                    Array.Reverse(sizeBuffer);
                }
                int frameSize = BitConverter.ToInt32(sizeBuffer, 0);

                // Validate frame size to avoid overflow
                if (frameSize <= 0 || frameSize > 1_000_000)
                {
                    //Debug.LogError($"Invalid frame size: {frameSize}. Skipping this frame.");
                    return;
                }

                // Allocate buffer and read frame data
                byte[] frameData = new byte[frameSize];
                bytesRead = 0;
                while (bytesRead < frameSize)
                {
                    int read = stream.Read(frameData, bytesRead, frameSize - bytesRead);
                    if (read == 0) break;  // Connection was closed
                    bytesRead += read;
                }

                if (bytesRead == frameSize)
                {
                    //Debug.Log($"Successfully received frame of size {frameSize} bytes");

                    texture.LoadImage(frameData);
                    videoDisplay.texture = texture;
                    videoDisplay.SetAllDirty();  // Force update to the UI

                    // Save the frame for debugging purposes
                    // System.IO.File.WriteAllBytes("received_frame.jpg", frameData);
                    // Debug.Log("Saved received frame to disk.");
                }
                else
                {
                    Debug.LogWarning("Did not receive the full frame data.");
                }
            }
        }
        catch (System.Exception e)
        {
            string g = ""; 
            //Debug.LogError("Error receiving video frame: " + e);
        }
    }
    public void SendToPython(string message)
    {
        if (client != null && client.Connected)
        {
            byte[] messageBytes = Encoding.UTF8.GetBytes(message + "\n");
            stream.Write(messageBytes, 0, messageBytes.Length);
            Debug.Log($"Sent message to Python: {message}");
        }
    }

    public void OnApplicationQuit()
    {
        stream.Close();
        client.Close();
    }
}
