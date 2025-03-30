# ContactTracingAppHooHacks

## Inspiration  
In a world where we’re constantly moving and interacting, it’s difficult to stay aware of potential exposure risks. By using technology and real-time data, we aim to enhance disease prevention, helping people make informed decisions to protect themselves and others.

## What it does  
Our application provides an interactive platform where we utilize user movement history to distribute notifications to users in close proximity to someone who later reports an illness, and report any physical interactions they may have had with someone to notify them anonymously.

## How we built it  
- **Backend**: Built with Django, handling user authentication using Google OAuth.  
- **Frontend**: Uses a mix of HTML, CSS, and JavaScript  
- **Database**: Stores user locations, timestamps, and exposure reports using PostgreSQL.  
- **Mapping & Visualization**: Folium and GeoJSON  
- **UI Design**: Figma

## Challenges we ran into  
We ran into several issues related to version control and rebasing main onto our branches. Additionally, some features we had in mind we found out were not possible to implement in a timely manner or were not possible at all.

## Accomplishments that we're proud of  
We were able to fulfill the main objective of our project—utilizing device location and time to notify users who were in close proximity to a user with an illness. Additionally, we were able to style our website well and display the location using libraries we had little to no familiarity with.

## What we learned  
We learned how location tracking and location intersections work, and how to utilize libraries to visualize the algorithms we used. Additionally, we learned about ways to efficiently work with version controlling and time/work delegation.

## What's next for HoosSick  
With more time, we plan on improving our proximity algorithm to best match the infectious nature of the differing diseases we loaded onto our database. We would also utilize Bluetooth for better location tracking and encryption for our data.
