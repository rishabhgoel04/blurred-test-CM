#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
sys.path.append('/home/ubuntu/purushottam')


# In[3]:


from helper import *
from import_modules import *


# In[5]:


df=get_data_cmdb("""
select * from order_items limit 10""")


# In[6]:


df


# In[10]:


paste_data_google_sheet(df,'1u8Sd3mEzIey1qbLV5mfyhZjWBss6GUc6rJxsb_XDjLA','Sheet1',1,1)


# In[ ]:





# In[ ]:




