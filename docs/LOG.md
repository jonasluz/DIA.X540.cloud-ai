# Report of the AI Services Experiments.

## Vision AI on Microsoft Azure.
1. At first, we decided to experiment with the facial recognition services.
2. We then, created a new Face Detector API service, part of Azure's Cognitive Services.
3. The objective was to send images of a face and detect the emotions depicted in them.
4. This was part in the objective of comparing the cloud providers AI services; the similar services from the competitors were to be used too.
5. But we faced the following related issues:
- In the [Quick Start Guide](https://learn.microsoft.com/pt-br/azure/ai-services/computer-vision/quickstarts-sdk/identity-client-library?tabs=windows%2Cvisual-studio&pivots=programming-language-python), we got a message explaining that some functionalities of the API required a request form to be filled. If not, the code woould not work apropriately.
- This was confirmed in the experiment using a Colab Python notebook that replicated the Quick Start code.
- Also, and more important, the aimed feature of emotional state recognition is not available anymore, as explained in the service [Overview page](https://learn.microsoft.com/pt-br/azure/ai-services/computer-vision/overview-identity). The justification is based on the [Responsible AI use argument](https://azure.microsoft.com/en-us/blog/responsible-ai-investments-and-safeguards-for-facial-recognition/).
6. So, we gave up on comparing the facial recognition services, as the Azure correspondent service is severed limited.