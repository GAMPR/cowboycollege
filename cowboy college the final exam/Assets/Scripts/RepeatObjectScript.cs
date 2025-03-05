using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RepeatObjectsScript : MonoBehaviour
{

    public float speed;
    public int wait_time;
    private int wait_count = 0;
    private bool at_start = false;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (!at_start) {transform.position += Vector3.left * speed;}
        else {
            if (wait_count < wait_time) {
                wait_count += 1;
            } else {
                wait_count = 0;
                at_start = false;
            }
            
        }

        
        if (transform.position.x <= -10) {
            transform.position = new Vector3(11, transform.position.y, transform.position.z);
            at_start = true;
        }

    }

}

