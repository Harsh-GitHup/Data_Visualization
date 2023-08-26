The userdata.json file contains a list of objects, each of which represents a user. Each user object has three properties: name, email, and message.

The following code loads the data from the userdata.json file into a Python list:

```python
import json

with open('userdata.json') as f:
  data = json.load(f)
```

The next step is to print the data to the console. We can do this using the following code:

```python
for user in data:
  print(user['name'])
  print(user['email'])
  print(user['message'])
```

The output of the code will be the following:

```
Harsh Kesharwani
harshkesharwani037@gmail.com
hello

Vikas Kushwaha
vikaskushwaha969113@gmail.com
9685105457
my mob. no.

Harsh Kesharwani
dx38xjz2@freeml.net
hii
jpt

Sahil Ullah
Sahil032@gmail.com
Hello Harsh I am Sahil my mobile no. is 7389597443

Altaf Mansuri
altafmansuri@gmail.com
Hello harsh! how are you?

Happy Jonson
dx38xjz2@freeml.net
hello

Happy Jonson
9a3ej@klovenode.com
History of India

Bhopali
Bhopali@gmail.com
Hii i am bhopali

vikas kushwaha
vikaskushwaha3@gmail.com
hello

Vivek
vivek@gmail.com
I Am vivek

Jayshree
Jayshree1401@gmail
Good Work In This website.
```