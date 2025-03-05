using UnityEngine;
using static UnityEngine.Random;
using System.Net.Sockets;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;

public class GetVideoScript2 : MonoBehaviour
{
    public RawImage videoDisplay;
    public GameObject menu;
    public GameObject drawText;
    public GameObject players;
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
                    //Debug.Log($"received frame. {frameSize} bytes");

                    texture.LoadImage(frameData);
                    videoDisplay.texture = texture;
                    videoDisplay.SetAllDirty();  // Force update to the UI

                    // Save the frame for debug
                    // System.IO.File.WriteAllBytes("received_frame.jpg", frameData);
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
            // If starting new round, pick random timer number for unity and send it to python
            if (message == "restart")
            {
                int countdown = Range(5, 16); //5-15
                message = string.Concat(message, countdown);
                StartCoroutine(HideGui(countdown));
            }

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

    IEnumerator HideGui(float duration)
    {
        menu.SetActive(false);
        players.SetActive(true);
        yield return new WaitForSeconds(duration);
        drawText.SetActive(true);
        yield return new WaitForSeconds(2);
        drawText.SetActive(false);
        yield return new WaitForSeconds(5);
        menu.SetActive(true);
        players.SetActive(false);
    }
}
