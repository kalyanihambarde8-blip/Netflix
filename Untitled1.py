#!/usr/bin/env python
# coding: utf-8

# In[19]:


import pandas as pd
import matplotlib.pyplot as plt


# In[17]:


netflix=pd.read_csv("Netflix_100_Customers_Dataset.csv")


# In[3]:


netflix


# In[4]:


# data cleaning method
netflix.shape # is used for find how many rows and columns


# In[5]:


netflix.info() # is use for find all information of data like data type and null values


# In[6]:


netflix.isnull() .sum() # to check total null values in data 


# In[7]:


netflix.duplicated().sum()


# In[8]:


netflix.describe() # is used for see statistical information in dataset


# In[14]:


netflix["Watch_Date"]=pd.to_datetime(netflix["Watch_Date"])


# In[15]:


netflix


# In[12]:


netflix


# In[13]:


netflix.dtypes


# In[21]:


netflix.groupby("Region")["Monthly_Revenue"].sum().plot(kind="bar",ylabel="Monthly_Revenue",title="region wise revenue")


# In[23]:


netflix.groupby("Subscription_Plan")["Rating"].sum().plot(kind="pie",title="Subscription_Plan wise rating")


# In[24]:


netflix.groupby("Category")["Rating"].sum().plot(kind="bar",ylabel="Category",title="category wise rating")


# In[ ]:


netflix.groupby("Category")["Rating"].sum().plot(kind="pie",title="category wise rating")

