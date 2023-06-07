import cv2
import pytesseract
import numpy as np
import discord

def IdentifyGame(image):
    print('IdentifyGame initiated')
    end = False
    detected = False 
    title = 'Unrecognised'
    while end == False:

        result = getText(image, 'SHOTS FIRED', 'CSGO') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'FLASH STATS', 'CSGO') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'Duration', 'CSGO') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break


        result = getText(image, 'TEAM 1', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'TEAM 2', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'TEAM1', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'TEAM2', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'VIEW ADVANCED DETAILS', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Summoner', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Howling Abyss', 'League of Legends')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'Operator Kills', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'PLAY WITH SQUAD AGAIN?', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'SQUAD TOTALS', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'Contracts', 'Warzone 1.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break


        result = getText(image, 'Cash spent', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'PLAY WITH SQUAD AGAIN', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'KORTAC', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'SCOREBOARD', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'DEFENDS', 'COD MW2 Multiplayer') #@#@#@#@#@#@#@@#@#
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'SPECGRU', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'DIVISION', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'VICTORY STREAK', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break








       # result = getText(image, 'REGION', 'XDefiant') #@#@#@#@#@#@#@@#@#
       # if result is not None:
      #      exist, title = result
      #  else: exist = result
      #  if exist:
      #      detected = True
       #     break








       # result = imageWithin(image, 'warzone_template2.png', 'Warzone 2.0')
      #  if result is not None:
     #       exist, title = result
      #  else: exist = result
     #   if exist:
      #      detected = True           
     #       break













        result = getText(image, 'Return to Orbit', 'Destiny 2') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'The Crucible', 'Destiny 2') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'WITH SQUAD', 'Apex Legends') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Revieve Given', 'Apex Legends') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Respawn Given', 'Apex Legends') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
       # result = imageWithin(image, 'apex_temp.PNG', 'Apex Legends')
        #if result is not None:
         #   exist, title = result
        #else: exist = result
        #if exist:
        #    detected = True
        #    break
  #      result = imageWithin(image, 'apex_temp2.PNG', 'Apex Legends')
   #     if result is not None:
    #        exist, title = result
     #   else: exist = result
      #  if exist:
       #     detected = True
        #    break

        result = getText(image, 'Battle Tasks', 'War Thunder') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Convertible', 'War Thunder') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = getText(image, 'Mission Accomplished', 'War Thunder') 
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = getText(image, 'Contracts', 'Warzone 1.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = imageWithin(image, 'mp_temp.png', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break


        result = imageWithin(image, 'warzone_template22.png', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True           
            break
        result = imageWithin(image, 'warzone_template222.png', 'Warzone 2.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True           
            break

        result = imageWithin(image, 'warzone1_temp.PNG', 'Warzone 1.0') #@#@#@@
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break

        result = imageWithin(image, 'mp_ranked_temp.png', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        result = imageWithin(image, 'mp_ranked_temp2.png', 'COD MW2 Multiplayer')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break



        result = imageWithin(image, 'warzone1_temp.PNG', 'Warzone 1.0')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break



      #  result = imageWithin(image, 'temp_xdefiant.PNG', 'XDefiant') #$#$#$#
      #  if result is not None:
      #      exist, title = result
     #   else: exist = result
     #   if exist:
     #       detected = True
    #        break
    #    end = True

        result = imageWithin(image, 'fortnite_template.PNG', 'Fortnite')
        if result is not None:
            exist, title = result
        else: exist = result
        if exist:
            detected = True
            break
        end = True

    return title


def getText(image, search, game):
    # Load the image in grayscale
    img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

# Define the specific text to search for
    search_text = search

# Use Tesseract to extract text from the image
    text = pytesseract.image_to_string(img)

# Check if the specific text is in the extracted textz
    if search_text in text:
        print(game)
        exist = True
        title = game
        return exist, title
    #else: print(text)

    
def imageWithin(image, temp, game):
   try:
    # Load the template image and the larger image to search within
    template_img = cv2.imread(temp)
    search_img = cv2.imread(image)

    # Convert the images to grayscale
    template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    search_gray = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)

    # Create a SIFT object
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors in the template image and the larger image
    kp1, des1 = sift.detectAndCompute(template_gray, None)
    kp2, des2 = sift.detectAndCompute(search_gray, None)

    # Create a Brute-Force Matcher object
    bf = cv2.BFMatcher()

    # Match the descriptors
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # Check if enough good matches were found
    if len(good_matches) > 12:
        # Extract the matched keypoints
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Find the perspective transform between the template image and the larger image
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Get the dimensions of the template image
        h, w = template_img.shape[:2]

        # Create a set of points representing the corners of the template image
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Apply the perspective transform to the points representing the corners of the template image
        dst = cv2.perspectiveTransform(pts, M)

        # Draw a polygon around the matched object in the larger image
        cv2.polylines(search_img, [np.int32(dst)], True, (0, 0, 255), 3, cv2.LINE_AA)

        print(game)
        Found = True
        title = game
        return Found, title
   except: return
