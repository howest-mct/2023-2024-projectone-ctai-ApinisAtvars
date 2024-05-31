# Project Information

**FIRST NAME LAST NAME:** Atvars Apinis

**Sparring Partner:** Viola Nguyen

**Project Summary in max 10 words:** AI that can distinguish between people walking in or out.

**Project Title:** AI Powered Classroom Occupation Meter

# Tips for Feedback Conversations

## Preparation

> Determine for yourself what you would like feedback on. Write down a few points in advance where you definitely want to receive feedback. This way, the feedback conversation will be more focused and the questions you definitely want answered will be addressed.

## During the Conversation:

> **Listen actively:** Do not immediately go on the defensive but try to listen well. Show both verbally and non-verbally that you are paying attention to the feedback by maintaining an open posture (eye contact, upright posture), taking notes, nodding...

> **Take notes:** Write down the feedback so you have it later. Note the key words and find a quick notation method for yourself. If you take good notes, you can briefly review your main feedback points at the end of the conversation.

> **Summarize:** Do not wait for a summary from the instructors, this is your task: Check if you have understood the message correctly by actively listening and summarizing in your own words.

> **Be open to the feedback:** Do not wait for a summary from the instructors, this is your task: Check if you have understood the message correctly by actively listening and summarizing in your own words.

> **Think about it:** Consider what you are going to do with the feedback and follow up. Do you find the comments justified or unjustified? Do you recognize yourself in the feedback? How are you going to address this?

## AFTER THE CONVERSATION

> Reread your notes and create action points. Make choices from all the feedback you received: What can you work on and what will you set aside for now. What were the priorities? Review the assignment sheet again to determine your focus points. Write your action points on the feedback sheet.

# Feedforward Conversations

## Conversation 1 (Date: 23/05/2024)

Lecturer: Marie Dewitte

Questions for this conversation:

- Question 1: How do I collect the data? 20% of it needs to be collected by me, how do I do that?

- Question 2: How do I classify whether a person is walking in or out? 2 classes, one facing the camera and one not?

- Question 3: How do I gauge accuracy? Percentage of people actually in the room or whether it's correct or not?

This is the feedback on my questions.

- Feedback 1: Hang a camera on top of the entrance of the classroom and take a video.

- Feedback 2: Using 2 counters for going in and going out. List with a number for people who are inside the classroom and add/deduct people. Be careful: angle! You should be able to see the whole classroom in the picture. First: person detector, then adding counters.

- Feedback 3: Accuracy can be gauged by judging whether a person was correctly identified. Accuracy score of >= 90% is good enough for this project.

## Conversation 2 (Date: 29/05/2024)

Lecturer: Marie Dewitte

Questions for this conversation:

- Question 1: Should I have a database for this project?

- Question 2: Is it normal to lose all of my data after I run out of computing credits? How do I get it back/can I do that?

- Question 3: Where do I see how much computing time I have left for the day?

- Question 4: Can I delete my Roboflow project if I have it downloaded, and I want to annotate more data?

- Question 5: (If the answer to the first question is no) Which data annotation tools to use and how do import labels with them?

- Question 6: If I want to have real-time detection, is the nano architecture the only viable option, or could I move it up to small, or medium?

- Question 7: How do I make YOLO run on my GPU? Will that be faster than it running on my CPU?

- Question 8: How do I make the model in Google Colab use imported weights from a previous training run?


This is the feedback on my questions.

- Feedback 1: No, it's not necessary. It's nice to have it, the same as frontend for the application with Gradio Python.

- Feedback 2: You can't get it back after the session ends. When you are done training your model, you need to get the weights out ASAP.

- Feedback 3: I will look into that.

- Feedback 4: No, it's better to create a new account.

- Feedback 5: (I didn't ask this question)

- Feedback 6: The time needed to make predictions is around the same, however, the larger architectures will need more time to train.

- Feedback 7: I will look into that.

- Feedback 8: It needs to be able to get from your Google Colab environment as it is just a container. Mount your drive and store stuff there.

## Conversation 3 (Date: 31/05/2024)

Lecturer: Pieter-Jan Beeckman

Questions for this conversation:

- Question 1: Is the demo You showed us yesterday meant to send camera feed? If not, how could I send video feed to my laptop?

- Question 2: If I send the video through Ethernet to my laptop, will there be flickering?

- Question 3: I have gotten the X11 forwarding to work in PuTTY, but can I get it to work from the VS Code terminal?

- Question 4: My model will be running from my laptop, but the video feed will be coming from the raspi, could I somehow get the frames from the window that opens up when I do X11 forwarding, so that I can make predictions with my model on them?

- Question 5: Show him the line demo. If I press the mouse button for the first time, can I be able to draw a line from that position to the current mouse position, and then fix it when I press the mouse again?

This is the feedback on my questions.

- Feedback 1: You can send each frame encoded using Base64 encoding.

- Feedback 2: No, there will not be flickering.

- Feedback 3: Yes, it should work from there, even on Windows.

- Feedback 4: You could take screenshots from the window, but it's easier either to transfer the frames directly, or record from the laptop.

- Feedback 5: Yes, check the cv2.EVENT_MOUSEMOVE. Use it in the left mouse button callback function.
