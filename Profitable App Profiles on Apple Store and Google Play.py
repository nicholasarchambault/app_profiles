#!/usr/bin/env python
# coding: utf-8

# # Profitable App Profiles on App Store and Google Play
# by Nicholas Archambault
# 
# Between the Apple Store and Google Play, over 4 million apps are available for download.  This project seeks to understand which types of free apps are most likely to attract and maintain users.

# As of September 2018, there were approximately 2 million iOS apps available on App Store and 2.1 million Android apps on Google Play.
# 
# Since collection and analysis of so much data would take time and money, we will analyze a sample of this data to determine for developers which apps should be targeted for revenue-producing advertisement. 

# We start by reading in and opening the datasets for the App Store and Google Play.

# In[1]:


from csv import reader
apple = open("AppleStore.csv")
google = open("googleplaystore.csv")

apple = reader(apple)
google = reader(google)

apple = list(apple)
header_apple = apple[0]
apple = apple[1:]

google = list(google)
header_google = google[0]
google = google[1:]


# To make it easier to explore the two data sets, we'll first write a function named `explore_data()` that we can use repeatedly to explore rows in a more readable way. We'll also add an option for our function to show the number of rows and columns for any data set.

# In[2]:


def explore_data(dataset, start, end, rows_and_columns=False):
    dataset_slice = dataset[start:end]    
    for row in dataset_slice:
        print(row)
        print('\n') # Adds a new (empty) line after each row

    if rows_and_columns:
        print('Number of rows:', len(dataset))
        print('Number of columns:', len(dataset[0]))


# In[3]:


# Rows
print(len(apple))
print(len(google))

# Columns
print(len(apple[0]))
print(len(google[0]))


# At a glance, we can see that the Apple dataset has dimensions of 7,197 rows by 16 columns, and that the Google dataset has dimensions of 10,841 rows by 13 columns.

# ## Deleting Incorrect Data
# The row 10,472 in the Google dataset corresponds to the app Life Made WI-Fi Touchscreen Photo Frame, and we can see that the rating is 19. This is clearly off because the maximum rating for a Google Play app is 5. As such, we'll delete this row.

# In[4]:


del google[10472]


# ## Removing Duplicate Entries
# ### Part One
# If we explore the Google Play data set long enough, we'll find that some apps have more than one entry. In total, there are 1,181 cases where an app occurs more than once, and 9,659 unique apps.

# In[5]:


duplicate_apps = []
unique_apps = []
for i in google:
    name = i[0]
    if name in unique_apps:
        duplicate_apps.append(name)
    else:
        unique_apps.append(name)
print("Duplicate apps: {}".format(len(duplicate_apps)))
print("Unique apps: {}".format(len(unique_apps)))


# We don't want to count certain apps more than once when we analyze data, so we need to remove the duplicate entries and keep only one entry per app.
# 
# The main difference between duplicate apps occurs on the fourth position of each row, which corresponds to the number of reviews. The different numbers show that the data was collected at different times. We can use this to build a criterion for keeping rows. We won't remove rows randomly, but rather we'll keep the rows that have the highest number of reviews because the higher the number of reviews, the more reliable the ratings.

# ### Part Two
# To remove duplicate rows, we can first initialize a dictionary showing the name and highest number of reviews for each unique app. 

# In[6]:


reviews_max = {}
for i in google:
    name = i[0]
    n_reviews = float(i[3])
    if name in reviews_max and reviews_max[name] < n_reviews:
        reviews_max[name] = n_reviews
    elif name not in reviews_max:
        reviews_max[name] = n_reviews
len(reviews_max)


# Next, we'll initialize two lists. For every app in the data set, we'll add the row to `google_clean` and the name to the `already_added` if the number of reviews matches the maximum for that app and if the app has not already been added. 

# In[7]:


google_clean = []
already_added = []
for i in google:
    name = i[0]
    n_reviews = float(i[3])
    if n_reviews == reviews_max[name] and name not in already_added:
        google_clean.append(i)
        already_added.append(name)
len(google_clean)


# We find a dictionary length of 9,659, as expected.

# ## Removing Non-English Apps
# Some app names are not in English, indicating that the apps do not target English-speaking audiences.  We'll remove those apps.
# 
# We have determined that the apps to be eliminated include all those with more than three non-English text characters based on ASCII classification. We can create a function that will determine whether an app should be removed. 

# In[8]:


def language(string):
    num = 0
    for i in string:
        if ord(i) > 127:
            num += 1
    if num > 3:
        return False
    return True


# In[9]:


# Test cases
print(language("Instagram"))
print(language("爱奇艺PPS -《欢乐颂2》电视剧热播"))
print(language("Docs To Go™ Free Office Suite"))
print(language("Instachat 😜"))


# The boolean mask that's been created can then be applied to both datasets to remove all non-English apps.

# In[10]:


english_apps_google = []
for i in google_clean:
    choice = language(i[0])
    if choice == True:
        english_apps_google.append(i)
print(len(english_apps_google))


# In[11]:


english_apps_apple = []
for i in apple:
    choice = language(i[1])
    if choice == True:
        english_apps_apple.append(i)
print(len(english_apps_apple))


# We're left with 9,614 Android apps and 6,183 Apple apps.

# ## Isolating Free Apps
# 
# To continue our analysis of which apps ought to be targeted for revenue-producing advertisements, we must filter the datasets to include only free apps.

# In[12]:


free_apple = []
for i in english_apps_apple:
    if i[4] == '0.0':
        free_apple.append(i)
print(len(free_apple))


# In[13]:


free_google = []
for i in english_apps_google:
    if i[7] == '0':
        free_google.append(i)
print(len(free_google))


# The datasets now contain 3,222 Apple apps and 8,864 Android apps.

# ## Most Common Apps by Genre
# 
# As previously mentioned, our aim is to understand which types of apps are most likely to attract users in order to target advertisements appropriately. 
# 
# To minimize risks and overhead, the validation strategy for an app idea is comprised of three steps:
# 
#    1. Build a minimal Android version of the app, and add it to Google Play.
#    2. If the app has a good response from users, we then develop it further.
#    3. If the app is profitable after six months, we also build an iOS version of the app and add it to the App Store.
# 
# Because our end goal is to add the app on both the App Store and Google Play, we need to find app profiles that are successful on both markets. For instance, a profile that might work well for both markets might be a productivity app that makes use of gamification.
# 
# We can begin our analysis by getting a sense of the most common genres for each market. For this, we'll build a frequency table for the `prime_genre` column of the App Store data set, and the `Genres` and `Category` columns of the Google Play data set.

# In[14]:


# Generate frequency tables that show percentages.
def freq_table(dataset, index):
    mydict = {}
    for i in dataset:
        column = i[index]
        
        if column in mydict:
            mydict[column] += 1
        else:
            mydict[column] = 1
    
    for j in mydict:
        mydict[j] /= len(dataset)
        mydict[j] *= 100
        mydict[j] = round(mydict[j], 2)
    
    return mydict

# Display percentages in descending order.
def display_table(dataset, index):
    table = freq_table(dataset, index)
    table_display = []
    for key in table:
        key_val_as_tuple = (table[key], key)
        table_display.append(key_val_as_tuple)

    table_sorted = sorted(table_display, reverse = True)
    for entry in table_sorted:
        print(entry[1], ':', entry[0])


# ### Apple Apps

# In[15]:


display_table(free_apple, 11) # `prime_genre` column of Apple dataset


# We can see that among the free English apps, more than a half (58.16%) are games. Entertainment apps are close to 8%, followed by photo and video apps, which are close to 5%. Only 3.66% of the apps are designed for education, followed by social networking apps, which amount for 3.29% of the apps in our data set.
# 
# The general impression is that App Store (at least the part containing free English apps) is dominated by apps that are designed for fun (games, entertainment, photo and video, social networking, sports, music, etc.), while apps with practical purposes (education, shopping, utilities, productivity, lifestyle, etc.) are more rare. 

# ### Android Apps

# In[16]:


display_table(free_google, 9) # Category column


# The landscape seems significantly different on Google Play: there are not that many apps designed for fun, and it seems that a good number of apps are designed for practical purposes (family, tools, business, lifestyle, productivity, etc.). The popularity of practical apps is confirmed by the frequency table we see for the Genres column:

# In[17]:


display_table(free_google, 1) # Genre column


# The difference between the Genres and the Category columns is not crystal clear, but one thing we can notice is that the Genres column is much more granular. We're only looking for the bigger picture at the moment, so we'll only work with the Category column moving forward.
# 
# Up to this point, we found that the App Store is dominated by apps designed for fun, while Google Play shows a more balanced landscape of both practical and for-fun apps. Now we'd like to get an idea about the kind of apps that have most users.

# ## Most Popular Apps by Genre on App Store
# 
# One way to find out what genres are the most popular is to calculate the average number of installs for each app genre. For the Google Play data set, we can find this information in the `Installs` column, but for the App Store data set this information is missing. As a workaround, we'll take the total number of user ratings as a proxy, which we can find in the `rating_count_tot` column.
# 
# Below, we calculate the average number of user ratings per app genre on the App Store:

# In[18]:


# Define list of genres
genre_list = []
for i in free_apple:
    genre = i[11]
    if genre not in genre_list:
        genre_list.append(genre)

print(genre_list)   


# In[19]:


# Increment counts for each genre
for genre in genre_list:
    total = 0
    len_genre = 0
    
    for i in free_apple:
        genre_app = i[11]
        
        if genre_app == genre:
            ratings = float(i[5])
            total += ratings
            len_genre += 1
    avg_ratings = total/len_genre
    print(genre, ":", round(int(avg_ratings), 0))


# On average, navigation, social networking, and music apps garner the highest number of user reviews.  These results, however, are skewed by the top apps that dominate each category, including Waze and Google Maps for navigation; Facebook, Pinterest and Skype for social networking; and Pandora, Spotify, and Shazam for music.

# In[20]:


# Define list of genres
for app in free_apple:
    if app[-5] == 'Navigation':
        print(app[1], ':', app[5])


# In[21]:


# Increment count for each genre
for app in free_apple:
    if app[-5] == 'Social Networking':
        print(app[1], ':', app[5])


# In[22]:


# Check listings of Music apps and find that it is dominated by a few apps, especially Pandora and Spotify
for app in free_apple:
    if app[-5] == 'Music':
        print(app[1], ':', app[5])


# Other popular genres include reference, weather, and food & drink. The reference genre is dominated by the Bible and dictionary apps, but holds promise for our app development goals.  Based on other high-performing apps in that category, it seems feasible and potentially successful to create an app version of a popular book, accompanied by additional materials besides the raw book text. Such materials could include audio quizzes, daily quotes, or authorial interviews. 
# 
# Since the market appears to be dominated by fun-focused apps, a more practical app like this may have the opportunity to stand out.

# ## Most Popular Apps by Genre on Google Play

# In[23]:


# Understand app installation popularity on Google Play
display_table(free_google, 5)


# A problem with this data is that the number of installs is not precise enough. To extract more meaningful data, we'll convert all these figures to floats.

# In[24]:


# Define list of categories
categories = []
for i in free_google:
    category = i[1]
    if category not in categories:
        categories.append(category)

print(categories)


# In[25]:


# Increment counts for each category
for category in categories:
    total = 0
    len_category = 0
    
    for i in free_google:
        category_app = i[1]
        
        if category_app == category:
            installs = i[5]
            installs = installs.replace("+", "")
            installs = installs.replace(",", "")
            installs = float(installs)
            total += installs
            len_category += 1
    
    avg_installs = total/len_category
    print(category, ":", round(int(avg_installs), 0))


# On average, communication apps have the most installs: 38,456,119. This number is heavily skewed up by a few apps that have over one billion installs (WhatsApp, Facebook Messenger, Skype, Google Chrome, Gmail, and Hangouts), and a few others with over 100 and 500 million installs:

# In[26]:


# View most-installed apps
for app in free_google:
    if app[1] == 'COMMUNICATION' and (app[5] == '1,000,000,000+'
                                      or app[5] == '500,000,000+'
                                      or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# We find the same pattern holds for video, social, photography, and productivity apps, the next four most popular genres. Each is dominated and has its data skewed higher by the presence of a few apps that have been installed millions or billions of times.
# 
# It would be hard for a newly developed app to compete agains the established giants that rule these categories. And as with the Apple store, the game market seems nearly saturated with options.
# 
# With an average of 8,767,811 installs, the books and reference genre seems to be worth exploring, as it was on the Apple store. 

# In[27]:


for app in free_google:
    if app[1] == 'BOOKS_AND_REFERENCE':
        print(app[0], ':', app[5])


# The book and reference genre includes a variety of apps: software for processing and reading ebooks, various collections of libraries, dictionaries, tutorials on programming or languages, etc. It seems there's still a small number of extremely popular apps that skew the average:

# In[28]:


for app in free_google:
    if app[1] == 'BOOKS_AND_REFERENCE' and (app[5] == '1,000,000,000+'
                                            or app[5] == '500,000,000+'
                                            or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# However, it looks like there are only a few very popular apps, so this market still shows potential.

# ## Conclusion
# 
# In this project, we analyzed data about the App Store and Google Play mobile apps with the goal of recommending an app profile that can be profitable for both markets.
# 
# We concluded that taking a popular book (perhaps a more recent book) and turning it into an app could be profitable for both the Google Play and the App Store markets. The markets are already full of libraries, so we need to add some special features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes on the book, a forum where people can discuss the book, etc.
