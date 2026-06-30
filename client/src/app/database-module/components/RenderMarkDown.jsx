import Markdown from "react-markdown";
import React, { useEffect } from "react";
import remarkGfm from "remark-gfm";

export const addCopyButton = (pre) => {
  const button = document.createElement("button");
  button.className = "copy-btn";
  button.innerText = "Copy";
  button.onclick = () => {
    const code = pre.querySelector("code")?.innerText || pre.innerText;
    navigator.clipboard
      .writeText(code)
      .then(() => {
        button.innerText = "Copied!";
        setTimeout(() => (button.innerText = "Copy"), 2000);
      })
      .catch(console.error);
  };
  pre.appendChild(button);
};

const RenderMarkDown = ({ description }) => {
  useEffect(() => {
    document.querySelectorAll("pre").forEach((pre) => {
      if (!pre.querySelector(".copy-btn")) addCopyButton(pre);
    });
  }, [description]);

  return (
    <>
      {description ? (
        <div className="markdown-container">
          <Markdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: (props) => (
                <a {...props} target="_blank" rel="noopener noreferrer" />
              ),
            }}
          >
            {description}
          </Markdown>
        </div>
      ) : (
        <p>No Setup Guide found!!</p>
      )}
    </>
  );
};

export default RenderMarkDown;
