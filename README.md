""Aims""
The main aim of this project is to build an AI-based system capable of identifying malicious packets and unusual network behaviours in real-time. This system will address the limitations in traditional cybersecurity tools when it comes to identifying evolving or new threats by utilizing advanced machine learning algorithms, which will mitigate emerging cyber threats while providing recommendations and actions to take to the users of the system when they are under attack.

""Objectives""
Data Collection: capture normal and anomalous network traffic data using wireshark to create a dataset which will be used for training and testing the machine learning model.
Controlled Cyber attacks: do some basic cyber attacks in an isolated environment to collect the anomalous data for training and testing.
Data labeling: process and label the collected data to ensure it’s suitable for training.
Model Development: create a machine learning model which is able to analyze large-scale network data to differentiate between normal and malicious packets.
User Guidance: Integrate functionalities to inform the users about the incoming threats and give recommendations on what to do next.
Testing: test the capabilities of the system using real-time scenarios.



""Project Limitations""
Data Dependence: the performance of the model is highly dependent on the quality of the dataset. Insufficient data might affect its ability to detect certain anomalies accurately.
Real-Time Constraint: since the system is designed and implemented to work in real time, high network volumes may introduce latency, which might make the identification and reporting of the threats a bit slow.
False Positives and Negatives: sometimes the system might classify safe packets as anomalous and vise-versa.
User Understanding: although the system will try to ensure user-friendliness, non-technical users might still find it difficult to understand some recommendations given by the system.
Recourse Limitations: the machine learning algorithms used might need high levels of hardware resources, which will limit training and processing on low level devices.

""Data Collection""
To create an effective AI-powered anomaly detection system, a high quality dataset is needed. That is why normal and anomalous data is manually collected using real network scenarios instead of using already existing datasets. Here is how:
Normal packet data: Normal packet data was captured using tshark (which wireshark built for terminal usage), the data was diverse which included data from every day to day operations like watching youtube, using whatsapp, going through emails… etc.
Anomalous packet data: The anomalous packets was captured using real cyber attacks in a controlled environment that does not harm any device, we have taken every measure to ensure no device gets harmed and the purpose of it is only to collect data, the process of capturing the anomalous data is done using tshark too.

""Data Preprocessing and Labeling""
Raw network data that was collected using tshark will be prepared to train the machine learning model. The steps include:
Extracting key features of the packets like source and destination IP, length of the packets, port numbers, and timestamps.
Removing any irrelevant features from the captured data.
Labeling the data as anomalous or normal packets.


""Testing and Evaluation""
The system was tested in a real-time network environment, specific attacks like Denial of Service (DoS) and port scans were used to evaluate the detection accuracy of the system. The system was evaluated using metrics for accuracy and speed. 

""User Guidance""
To create the system in a way that everyone can use and understand it, a user-friendly interface was developed that included key features like real time monitoring, choosing the preferred languages, and giving recommendations in a way that even non technical people could understand and follow through it.

""Summary""
The methodology used in this project consisted of collecting good network data, preprocessing and labeling, developing an advanced AI model and creating a user friendly interface because in the end, it is the people using our system and we have taken their amount of education and technical knowledge into consideration.
