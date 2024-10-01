from datetime import timedelta, datetime
import aiofiles
import json
# Global data structure to store user activity
activity_data = {}

async def load_activity_data():
    global activity_data
    try:
        async with aiofiles.open('people_activity_record.json', 'r') as f:
            contents = await f.read()
            activity_data = json.loads(contents)
            # Convert string times back to datetime and float for duration
            for user_id, activities in activity_data.items():
                if 'start_time' in activities:
                    activities['start_time'] = datetime.fromisoformat(activities['start_time'])

                # Load the username if it's stored
                if 'username' in activities:
                    activities['username'] = activities['username']

                # Convert daily activity data from string to float
                for date_str, activity in activities['daily'].items():
                    for activity_name, time_str in activity.items():
                        hours, minutes, seconds = map(float, time_str.split(':'))
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        activity[activity_name] = total_seconds  # Store as float

                # Convert total activity data from string to float
                for activity_name, time_str in activities['total'].items():
                    hours, minutes, seconds = map(float, time_str.split(':'))
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    activities['total'][activity_name] = total_seconds  # Store as float
    except FileNotFoundError:
        print("No previous activity data found. Starting fresh.")
    except json.JSONDecodeError:
        print("Error decoding JSON data. Starting fresh.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to convert datetime objects to string for JSON serialization
def serialize_activity_data(data):
    serialized_data = {}
    for user_id, activities in data.items():
        serialized_data[user_id] = {
            'daily': {},
            'total': {},
            'username': activities.get('username', '')  # Save the username if it exists
        }

        # Convert daily activity data to formatted strings
        for date_str, activity in activities['daily'].items():
            serialized_data[user_id]['daily'][date_str] = {
                activity_name: str(timedelta(seconds=int(total_seconds))) 
                for activity_name, total_seconds in activity.items()
            }

        # Convert total activity data to formatted strings
        for activity_name, total_seconds in activities['total'].items():
            serialized_data[user_id]['total'][activity_name] = str(timedelta(seconds=int(total_seconds)))

        # Convert start_time to string if it exists
        if 'start_time' in activities:
            serialized_data[user_id]['start_time'] = activities['start_time'].isoformat()
        if 'current_activity' in activities:
            serialized_data[user_id]['current_activity'] = activities['current_activity']

    return serialized_data


# Async function to save activity data to a JSON file
async def save_activity_data():
    serialized_data = serialize_activity_data(activity_data)
    async with aiofiles.open('people_activity_record.json', 'w') as f:
        await f.write(json.dumps(serialized_data, indent=4))


async def trackActivity(before, after, role_ids_to_check, firstBoot):
    global activity_data
    if firstBoot:
        await load_activity_data()

    # Check if the user has the specific role
    user_role_ids = [role.id for role in after.roles]
    if not any(role_id in role_ids_to_check for role_id in user_role_ids):
        return  # If the user doesn't have the role, exit the function

    user_id = str(after.id)  # Get the user ID as a string for JSON serialization
    username = after.name # Get the user's display name
    current_date = datetime.now().date()  # Get the current date

    # Initialize the user's data if not already present
    if user_id not in activity_data:
        activity_data[user_id] = {
            'daily': {},
            'total': {},
            'username': username  # Store the username here
        }

    # Handle the end of an activity
    if after.activity is None:
        if user_id in activity_data and 'start_time' in activity_data[user_id]:
            end_time = datetime.now()
            duration = end_time - activity_data[user_id]['start_time']
            activity_name = activity_data[user_id]['current_activity']

            date_str = str(current_date)
            if date_str not in activity_data[user_id]['daily']:
                activity_data[user_id]['daily'][date_str] = {}

            if activity_name not in activity_data[user_id]['daily'][date_str]:
                activity_data[user_id]['daily'][date_str][activity_name] = 0

            seconds = duration.total_seconds()
            activity_data[user_id]['daily'][date_str][activity_name] += seconds

            if activity_name not in activity_data[user_id]['total']:
                activity_data[user_id]['total'][activity_name] = 0

            activity_data[user_id]['total'][activity_name] += seconds

            await save_activity_data()

            total_duration_today = activity_data[user_id]['daily'][date_str][activity_name]
            formatted_duration = str(timedelta(seconds=int(total_duration_today)))
            #await channel.send(f"User {username} (<@{user_id}>) has been active in '{activity_name}' for {formatted_duration} today.")

            del activity_data[user_id]['start_time']
            del activity_data[user_id]['current_activity']

    # Handle the start of a new activity
    if before.activity != after.activity:
        if after.activity is not None:  # If a new activity starts
            activity_data[user_id]['start_time'] = datetime.now()
            activity_data[user_id]['current_activity'] = after.activity.name
            #await channel.send(f"User <@{user_id}> is now active: {after.activity.name}")

    #print(activity_data)  # Print the activity data for debugging