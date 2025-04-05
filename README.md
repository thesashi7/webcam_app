# Setup Instructions
- Install Pipenv if not already. For mac -> ```brew install pipenv```
- Install dependecies -> ```pipenv install```
- Activate virtual env -> ```pipenv shell```
- Run the App -> ```uvicorn main:app```
- Go to -> ```http://localhost:8000/```

## Application features

***<ins>There are two tabs for webcam feeds: 1) Multiple Screens 2) Single Screen</ins>***
1) Multiple Screens
   - This shows BGR image, Gray scale , and Blue image channel simultaneously on the same UI side by side in real time
3) Single Screen
   - This by default shows a BGR image with the ability to change the grayscale intensity using the slider.
   - There is also a dropdown to change the channel between Red, Green, Blue, and BGR.

### Cache
- There is ability to replay the last 30 secs of webcam feed in the Multiple Screens tab only.
- Also, the cache resets everytime you start live feed. Which means cache will store last 30 secs from the recent live webcam feed only.
