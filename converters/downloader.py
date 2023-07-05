import gdown

url = "https://drive.google.com/file/d/1oCgHUkzY9EDk5zjT9K95gJpdc__ANRHV/view" 
output = "final_csv.zip"
gdown.download(url, output, quiet=False, fuzzy=True) 