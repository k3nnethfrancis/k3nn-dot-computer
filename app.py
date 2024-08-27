import os
from pathlib import Path
import uvicorn
import logging

import glob
import yaml
import markdown2

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv; load_dotenv()

from datetime import datetime, date
from image_generator import generate_post_image

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define paths for SSL certificates
# CERTS_DIR = "/Users/kenneth/Desktop/lab/k3nn.computer/certs"
# ssl_keyfile = os.getenv('SSL_KEYFILE', CERTS_DIR + '/key.pem')
# ssl_certfile = os.getenv('SSL_CERTFILE', CERTS_DIR + '/cert.pem')

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3333",
        "http://0.0.0.0:3333",
        "http://127.0.0.1:3333",
        "http://localhost:1337",
        "http://0.0.0.0:1337",
        "http://127.0.0.1:1337",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/components", StaticFiles(directory="components"), name="components")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Set up Jinja2 templates, now using the "pages" directory
pages = Jinja2Templates(directory="pages")

def read_markdown_files():
    posts = []
    for filepath in glob.glob("posts/*.md"):
        with open(filepath, "r") as file:
            content = file.read()
            _, frontmatter, body = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            
            title = body.strip().split('\n')[0].lstrip('# ').strip()
            
            # Handle the date whether it's a string or already a date object
            post_date = metadata["date"]
            if isinstance(post_date, str):
                post_date = datetime.strptime(post_date, "%Y-%m-%d").date()
            elif isinstance(post_date, date):
                post_date = post_date
            else:
                raise ValueError(f"Unexpected date format in {filepath}")

            posts.append({
                "title": title,
                "date": post_date,
                "tags": metadata.get("tags", []),
                "read_time": metadata.get("readTime", "N/A"),
                "filename": os.path.basename(filepath).replace(".md", "")
            })
    
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     if request.url.path.startswith("/ISAPI/"):
#         return JSONResponse(status_code=404, content={"message": "Not Found"})
#     return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    posts = read_markdown_files()[:3]  # Get the 3 most recent posts
    return pages.TemplateResponse("index.html", {"request": request, "recent_posts": posts})

@app.get("/listings", response_class=HTMLResponse)
async def read_listings(request: Request):
    posts = read_markdown_files()
    return pages.TemplateResponse("listings.html", {"request": request, "posts": posts})

@app.get("/post/{post_name}", response_class=HTMLResponse)
async def read_post(request: Request, post_name: str):
    logging.info(f"Accessing post: {post_name}")
    filepath = f"posts/{post_name}.md"
    if not os.path.exists(filepath):
        logging.error(f"Post not found: {filepath}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    with open(filepath, "r") as file:
        content = file.read()
        md = markdown2.Markdown(extras=["metadata"])
        html = md.convert(content)
        metadata = md.metadata
        
        # Generate image if it doesn't exist
        img_path = f"assets/img/{post_name}.png"
        if not os.path.exists(img_path):
            img_path = generate_post_image(content, metadata.get("title", post_name))
        
        # Ensure img_path is relative to the static directory
        img_path = img_path.replace("assets/", "")
        
        logging.info(f"Successfully rendered post: {post_name}")
        return pages.TemplateResponse(
            "post.html", 
            {
                "request": request, 
                "content": html, 
                "metadata": metadata,
                "img_path": img_path
            }
        )

@app.get("/timeline", response_class=HTMLResponse)
async def read_my_work(request: Request):
    return pages.TemplateResponse("timeline.html", {"request": request})

# Serve the terminal page
@app.get("/terminal", response_class=HTMLResponse)
async def terminal_page(request: Request):
    return pages.TemplateResponse("terminal.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3333,
        # Comment out SSL for now
        # ssl_keyfile=ssl_keyfile,
        # ssl_certfile=ssl_certfile
    )