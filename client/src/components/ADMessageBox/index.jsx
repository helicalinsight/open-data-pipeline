import { Button } from "antd";
import { SendOutlined, PauseCircleOutlined } from "@ant-design/icons";
import { useEffect, useRef, useState } from "react";
import { useSelector } from "react-redux";

import BeatLoader from "../ADLoader/BeatLoader/BeatLoader";
import ADFollowUpPrompt from "../ADFollowUpPrompt";
import Editor, { useMonaco } from "@monaco-editor/react";

import "./style.scss";

function ADMessageBox({ handleMessageSent, botStatus, columns, loadedFiles }) {
  const editorRef = useRef(null);
  const monacoInstance = useMonaco();
  const [editorValue, setEditorValue] = useState("");
  const [ediotorHeight, setEditorHeight] = useState(35);
  const [numberOfLines, setNumberOfLines] = useState();
  const [editPrompt, setEditPrompt] = useState(null);
  const selectedExtensions = useSelector(
    (store) => store.app.selectedExtensions
  );
  
  window.addEventListener("unhandledrejection", function (event) {
    if (event.reason && event.reason.type === "cancelation") {
      event.preventDefault();
    }
  });
  
  const getEditorAutoCompleteSuggestion = (range, chars) => {
    let suggestions = [];
    if (chars?.triggerCharacter === "/") {
      if (range?.startColumn === 2) {
        selectedExtensions.forEach((suggestion) => {
          suggestions.push({
            label: suggestion,
            kind: monacoInstance.languages.CompletionItemKind.Method,
            insertText: `${suggestion} `,
            range,
          });
        });
      }
    } else {
      loadedFiles.forEach((file) => {
        suggestions.push({
          label: file.alias,
          kind: monacoInstance.languages.CompletionItemKind.File,
          insertText: file.alias,
          range,
        });
      });
      columns?.forEach((col) => {
        suggestions.push({
          label: col,
          kind: monacoInstance.languages.CompletionItemKind.Variable,
          insertText: col,
          range,
        });
      });
    }

    const uniqueLabels = new Set();
    const resultArray = [];

    suggestions.forEach((item) => {
      if (!uniqueLabels.has(item.label)) {
        uniqueLabels.add(item.label);
        resultArray.push(item);
      }
    });

    return {
      suggestions: resultArray,
    };
  };

  useEffect(() => {
    let disposable = null;

    if (monacoInstance) {
      disposable = monacoInstance.languages?.registerCompletionItemProvider(
        "plaintext",
        {
          triggerCharacters: ["/"],
          provideCompletionItems: (model, position, chars) => {
            const word = model.getWordUntilPosition(position);

            const range = {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: word.startColumn,
              endColumn: word.endColumn,
            };

            return getEditorAutoCompleteSuggestion(range, chars);
          },
        }
      );
    }

    return () => {
      disposable?.dispose();
    };
  }, [columns, loadedFiles, monacoInstance]);

  useEffect(() => {
    if (editPrompt) {
      const text = JSON.stringify(editPrompt.data.value);
      setEditorValue(text);
    }
  }, [editPrompt]);

  useEffect(() => {
    return () => handleComponentWillUnmount();
  }, []);

  useEffect(() => {
    if (numberOfLines > 1) {
      const contentHeight = Math.min(
        1000,
        editorRef.current?.getContentHeight()
      );
      if (contentHeight) {
        setEditorHeight(contentHeight * 2);
      }
    }
  }, [numberOfLines]);

  useEffect(() => {
    if (botStatus === false) {
      editorRef?.current?.focus();
    }
  }, [botStatus]);

  function handleSend() {
    const editorValue = editorRef.current?.getValue();
    if (!editorValue?.length) {
      return;
    }
    if (editPrompt) {
      let payload = {
        isCustom: true,
        title: `Your columns are selected for ${editPrompt.data.type} transfromation`,
        message: editPrompt.response,
        type: null,
        value: `Your columns are selected for ${editPrompt.data.type} transfromation`,
        payload: {
          type: editPrompt.data.type,
          // prompt: editPrompt.data.prompt,
          value: editorValue,
        },
      };
      setEditPrompt(null);
      setEditorValue("");
      handleMessageSent(payload);
      return;
    }
    let data = {
      payload: editorValue,
      title: editorValue,
    };

    let type;
    for (const suggestion of selectedExtensions) {
      if (editorValue.startsWith(`/${suggestion}`)) {
        type = "/" + suggestion;
        break;
      }
    }

    if (type) {
      data.isCustom = true;
      data.type = type;
      data.payload = editorValue;
    }

    handleMessageSent(data);
    setEditorValue("");
  }

  const handleEditorDidMount = (editor, monaco) => {
    editor?.focus();

    let placeholderElement = document.querySelector(".monaco-placeholder");
    placeholderElement.style.display = "block";

    editorRef.current = editor;

    editor.addAction({
      id: "testing_a",
      label: "testing a",
      keybindings: [monaco.KeyCode.Enter],
      precondition: "!suggestWidgetVisible",
      run: handleSend,
    });

    editor.onDidChangeModelContent(() => {
      const numLines = editor.getModel().getLineCount();
      setNumberOfLines(numLines);
    });

    editor.onDidContentSizeChange((data) => {
      if (data.contentHeightChanged) {
        const contentHeight = Math.min(1000, editor.getContentHeight());
        setEditorHeight(contentHeight * 2);
      }
    });
  };

  const handleComponentWillUnmount = () => {
    if (editorRef.current) {
      editorRef.current.dispose(); // Dispose the editor instance
    }
  };

  const handleStopRequest = () => {
    // socket.emit("user_uttered", {
    //   message: "/abort_transformation",
    //   session_id: chatId,
    // });
  };

  const handleEditorOnChange = (value, ev) => {
    setEditorValue(value);

    // if there is a value, hide the placeholder...
    // else show it
    let placeholderElement = document.querySelector(".monaco-placeholder");
    if (!value) {
      placeholderElement.style.display = "block";
    } else {
      placeholderElement.style.display = "none";
    }
  };

  return (
    <>
      <section className="ad-message-container">
        {botStatus && (
          <div
            className="ad-message-container__is-typing-box"
            data-testid="beat-loader"
          >
            <div className="ad-message-container__typing-container">
              <Button
                type="text"
                onClick={handleStopRequest}
                icon={
                  <PauseCircleOutlined
                    style={{ fontSize: "18px", color: "rgb(242, 142, 30)" }}
                  />
                }
                data-testid="bot-abort-btn"
              />
              <span className="typing-text">{botStatus}</span>
              <BeatLoader size={5} color="#152A4F" />
            </div>
          </div>
        )}
        {!botStatus && (
          <div data-testid="follow-up-prompts">
            <ADFollowUpPrompt
              handleMessageSent={handleMessageSent}
              setEditPrompt={setEditPrompt}
            />
          </div>
        )}
        <div
          style={{
            cursor: botStatus !== false && "not-allowed",
          }}
          className={`editor-container dFlex alignCenter justifyBetween ${
            botStatus !== false ? "hide-cursor" : ""
          }`}
        >
          <Editor
            id="askondata"
            data-testid="ad-editor"
            height={`${ediotorHeight}px`}
            value={editorValue}
            width="98%"
            language="plaintext"
            theme="vs-light"
            onMount={handleEditorDidMount}
            className={`ad-message-container__input-box ${
              botStatus !== false ? "disabled-cursor" : ""
            }`}
            onChange={handleEditorOnChange}
            options={{
              lineNumbers: "off",
              minimap: { enabled: false },
              hideCursorInOverviewRuler: true,
              wordWrap: "on",
              automaticLayout: true,
              contextmenu: false,
              wrappingStrategy: "advanced",
              overviewRulerLanes: 0,
              scrollBeyondLastLine: false,
              scrollBar: {
                vertical: "hidden",
                horizontal: "hidden",
              },
            }}
          />
          <div className="monaco-placeholder"> Enter a prompt here </div>
          <SendOutlined
            style={{
              fontSize: "14px",
              color: "#152A4F",
            }}
            onClick={handleSend}
            className={`${botStatus !== false ? "disabled-cursor" : ""}`}
            data-testid="send-button"
          />
        </div>
      </section>
    </>
  );
}

export default ADMessageBox;
