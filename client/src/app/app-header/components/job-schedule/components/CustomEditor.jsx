import { Button, Skeleton, Space, message, Tooltip } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  getCode,
  runCode,
  updateCode,
} from "../../../../../apis/jobScheduleService";
import { handleSessionExpiry } from "../../../../../utils/handleSessionExpiry";
import { useDispatch, useSelector } from "react-redux";
import { setIsYamlSaved } from "../../../../../store/actions/chatAction";
import { imagePath } from "../../../../../constants/appConstants";
import { CloseOutlined, InfoCircleOutlined } from "@ant-design/icons";
import {
  triggerGetInfoAPI,
  triggerPipelineHistory,
} from "../../../../../apis/commonAPIs";
import SuppportBot from "./SuppportBot";
import Editor, { useMonaco } from "@monaco-editor/react";
import {
  setPreviewState,
  setSidebarState,
} from "../../../../../store/actions/appActions";
import { dispatchMessage } from "../../../../../utils/handleClick";
import CustomMessage from "../../../../settings-module/CustomMessage";
import { setHideMessageAction } from "../../../../../store/actions/settingActions";
import { v4 as uuidv4 } from "uuid";
import {
  getTopLevelDuplicateKeys,
  validateKeysRecursive,
  validKey,
} from "../../../../database-module/components/utils";
import { TOOLTIPS_INFO } from "../constants";
import YAML from "yaml";
import { isDmsRoute } from "../../../../../router/uiRouteConstants";
import { useLocation } from "react-router-dom";

const validatePythonIndentation = (code) => {
  const lines = code.split("\n"),
    errors = [],
    indentStack = [0];
  const blockStarters = [
    "if",
    "for",
    "while",
    "def",
    "class",
    "with",
    "try",
    "except",
    "else",
    "elif",
    "finally",
  ];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i],
      trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const currentIndent = line.search(/\S|$/);
    if (i > 0) {
      const prevLine = lines[i - 1].trim();
      const isBlockStarter = blockStarters.some(
        (s) =>
          prevLine.startsWith(s) &&
          (prevLine.endsWith(":") || prevLine.includes(": #"))
      );
      if (isBlockStarter && currentIndent <= lines[i - 1].search(/\S|$/)) {
        errors.push({
          line: i + 1,
          message: "Expected indented block after compound statement",
          severity: 8,
        });
      }
    }
    if (currentIndent % 4 !== 0 && currentIndent > 0) {
      errors.push({
        line: i + 1,
        message: "Indentation not multiple of 4 spaces",
        severity: 4,
      });
    }
    if (currentIndent > indentStack[indentStack.length - 1]) {
      indentStack.push(currentIndent);
    } else if (currentIndent < indentStack[indentStack.length - 1]) {
      while (
        indentStack.length > 1 &&
        currentIndent < indentStack[indentStack.length - 1]
      )
        indentStack.pop();
      if (currentIndent !== indentStack[indentStack.length - 1]) {
        errors.push({
          line: i + 1,
          message: "Unindent does not match outer level",
          severity: 8,
        });
      }
    }
  }
  return errors;
};

const formatYaml = (yamlText) => {
  try {
    const parsed = YAML.parse(yamlText);
    return YAML.stringify(parsed, {
      indent: 4,
      indentSeq: true,
      simpleKeys: false,
      lineWidth: 0,
    });
  } catch (error) {
    console.error("Error formatting YAML:", error);
    return formatYamlWithBasicIndentation(yamlText);
  }
};

const formatYamlWithBasicIndentation = (yamlText) => {
  let indent = 0;
  const indentSize = 4;
  return yamlText
    .split("\n")
    .map((line) => {
      const trimmed = line.trim();
      if (!trimmed) return "";
      if (trimmed.startsWith("-") && !trimmed.includes(":")) {
        indent = Math.max(0, indent - indentSize);
      }
      const formatted = " ".repeat(indent) + trimmed;
      if (
        (trimmed.endsWith(":") ||
          (trimmed.startsWith("-") && trimmed.includes(":"))) &&
        !trimmed.startsWith("#")
      ) {
        indent += indentSize;
      }
      return formatted;
    })
    .join("\n");
};

const CustomEditor = ({
  mode,
  open,
  onChildrenDrawerClose,
  selectedChat,
  onAdd,
  isJobConfig,
  wordWrap,
}) => {
  const dispatch = useDispatch();
  const location = useLocation();
  const monacoInstance = useMonaco();
  const editorRef = useRef();
  const [loading, setLoading] = useState(false);
  const [disable, setDisable] = useState(false);
  const [editorValue, setEditorValue] = useState("");
  const [messageApi, contextHolder] = message.useMessage();
  const [showSupportBot, setShowSupportBot] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [currWord, setCurrWord] = useState(""); // do not remove this
  const [prevWord, setPrevWord] = useState("");
  const [runState, setRunState] = useState(false);
  const [saveState, setSaveState] = useState(false);
  const [messages, setMessages] = useState([]);
  const [editorType, setEditorType] = useState("json");
  const isScheduleEditMode = useSelector(
    (state) => state.jobSchedule?.isScheduleEditMode
  );
  const jobListDetails = useSelector(
    (state) => state.jobSchedule?.jobListDetails
  );
  const editorSuggestions = useSelector((store) => store.app.editorSuggestions);
  const messageData = useSelector((store) => store?.settings?.messageData);
  const scheduleConfig =
    useSelector(
      (state) => state.chat?.chatList[selectedChat.chat_id]?.scheduleConfig
    ) ?? [];
  const selectedDmsChat = useSelector((state) => state.dms?.selectedDmsChat);
  const isDms = isDmsRoute(location.pathname);
  const dmsScheduleConfig =
    useSelector(
      (state) => state?.dms?.dmsJobs[selectedDmsChat?.chat_id]?.dmsScheduleConfig
    ) ?? [];
  const activeConfig = isDms ? dmsScheduleConfig : scheduleConfig;
  const formatDocument = () => {
    if (!editorRef.current) return;
    const model = editorRef.current.getModel();
    if (!model) return;
    const currentValue = model.getValue();
    if (mode === "yaml") {
      const formattedYaml = formatYaml(currentValue);
      setEditorValue(formattedYaml);
      editorRef.current.executeEdits("", [
        {
          range: model.getFullModelRange(),
          text: formattedYaml,
        },
      ]);
    } else if (mode === "json" || editorType === "json") {
      try {
        const parsedJson = JSON.parse(currentValue);
        const formattedJson = JSON.stringify(parsedJson, null, 2);
        setEditorValue(formattedJson);

        editorRef.current.executeEdits("", [
          {
            range: model.getFullModelRange(),
            text: formattedJson,
          },
        ]);
      } catch (error) {
        dispatchMessage(dispatch, "error", "Invalid JSON format");
      }
    }
  };

  const handleMount = (editor, monaco) => {
    editorRef.current = editor;
    editor.getModel()?.setEOL(monaco?.editor?.EndOfLineSequence?.CRLF);
    editor.addAction({
      id: "format-document",
      label: "Format Document",
      contextMenuGroupId: "navigation",
      contextMenuOrder: 1.5,
      run: () => {
        formatDocument();
      },
      keybindings: [
        monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF,
      ],
    });

    editor.onDidChangeModelContent(() => {
      const currentPosition = editor.getPosition();
      const wordInfo = editor.getModel().getWordAtPosition(currentPosition);
      const currentWord = wordInfo?.word || "";
      setCurrWord((prev) => {
        setPrevWord(prev);
        return currentWord;
      });
      if (mode === "python") {
        validatePythonCode(editor);
      }
    });
  };

  const validatePythonCode = (editor) => {
    if (!monacoInstance || mode !== "python") return;
    const model = editor.getModel();
    const code = model.getValue();
    monacoInstance.editor.setModelMarkers(model, "python", []);
    const indentationErrors = validatePythonIndentation(code);
    if (indentationErrors.length > 0) {
      const markers = indentationErrors.map((error) => ({
        severity: error.severity,
        startLineNumber: error.line,
        startColumn: 1,
        endLineNumber: error.line,
        endColumn: model.getLineLength(error.line) + 1,
        message: error.message,
      }));
      monacoInstance.editor.setModelMarkers(model, "python", markers);
    }
  };

  const getEditorAutoCompleteSuggestion = (range, chars, prevWord) => {
    let suggestions = [];
    let suggData = editorSuggestions[mode] || [];
    if (prevWord) {
      const wordData = suggData.find(
        (eachSugg) => prevWord?.toLowerCase() === eachSugg?.label?.toLowerCase()
      );
      if (wordData) {
        suggData = wordData.methods || [];
      }
    }
    suggData.forEach((eachSuggestion) => {
      suggestions.push({
        label: eachSuggestion?.label,
        kind: monacoInstance.languages.CompletionItemKind[eachSuggestion?.kind],
        detail: eachSuggestion?.detail,
        documentation: eachSuggestion?.documentation,
        insertText: eachSuggestion?.insertText,
        range,
      });
    });
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
        mode,
        {
          triggerCharacters: ["."],
          provideCompletionItems: (model, position, chars) => {
            const wordInfo = model.getWordUntilPosition(position);
            const range = {
              startLineNumber: position.lineNumber,
              endLineNumber: position.lineNumber,
              startColumn: wordInfo.startColumn,
              endColumn: wordInfo.endColumn,
            };
            return getEditorAutoCompleteSuggestion(range, chars, prevWord);
          },
        }
      );
    }
    return () => {
      disposable?.dispose();
    };
  }, [monacoInstance, editorSuggestions, prevWord]);

  useEffect(() => {
    if (!open) return;
    if (isScheduleEditMode) return;
    setLoading(true);
    getCode({
      chatId: isDms ? selectedDmsChat?.chat_id :selectedChat?.chat_id,
      onSuccess: (res) => {
        if (res.success) {
          if (mode === "python") {
            setEditorValue(res?.chats.code);
          } else if (mode === "yaml") {
            setEditorValue(res?.chats.history);
          }
        }
        setLoading(false);
      },
      onError: (err) => {
        handleSessionExpiry(dispatch, err);
        setLoading(false);
      },
    });
  }, [open]);

  // Config
  const initializedRef = useRef(false);
  useEffect(() => {
    const getFormattedConfig = (configArray) => {
      return configArray?.reduce((acc, { configKey, configValue }) => {
        try {
          let parsedValue;
          try {
            parsedValue = JSON.parse(configValue?.trim());
          } catch (e) {
            parsedValue = configValue;
          }
          acc[configKey] = parsedValue;
        } catch (error) {
          console.error("Error parsing configValue:", error);
        }
        return acc;
      }, {});
    };

    if (isJobConfig && !initializedRef.current) {
      if (
        isScheduleEditMode &&
        Array.isArray(jobListDetails?.job_details?.configuration)
      ) {
        const formattedConfig = getFormattedConfig(
          jobListDetails.job_details.configuration
        );
        setEditorValue(JSON.stringify(formattedConfig, null, 2));
        initializedRef.current = true;
      } else if (Array.isArray(activeConfig)) {
        const formattedConfig = getFormattedConfig(activeConfig);
        setEditorValue(JSON.stringify(formattedConfig, null, 2));
        initializedRef.current = true;
      }
    }
  }, [activeConfig, isJobConfig, isScheduleEditMode, jobListDetails]);

  const handleSaveJobTrigger = () => {
    try {
      const inputObject = JSON?.parse(editorValue.trim());
      const duplicates = getTopLevelDuplicateKeys(editorValue);
      if (duplicates.length > 0) {
        dispatchMessage(
          dispatch,
          "error",
          `Duplicate keys found: ${[...new Set(duplicates)].join(", ")}`
        );
        return;
      }
      if (!validateKeysRecursive(inputObject)) {
        dispatchMessage(
          dispatch,
          "error",
          "JSON contains empty or invalid key(s) at some level"
        );
        return;
      }
      for (const [configKey, configValue] of Object.entries(inputObject)) {
        const keyError = validKey(configKey);
        if (keyError) {
          dispatchMessage(
            dispatch,
            "error",
            `Invalid key "${configKey}": ${keyError}`
          );
          return;
        }
        if (
          configValue === null ||
          configValue === "" ||
          (typeof configValue === "object" &&
            Object?.keys(configValue)?.length === 0)
        ) {
          dispatchMessage(dispatch, "error", `Invalid value for key.`);
          return;
        }
      }
      const result = Object?.entries(inputObject).map(
        ([configKey, configValue]) => ({
          key: uuidv4(),
          configKey,
          configValue:
            typeof configValue === "string"
              ? configValue.trim()
              : JSON?.stringify(configValue).trim(),
        })
      );
      onAdd(result, "bulk");
      dispatchMessage(dispatch, "success", "Job config updated successfully");
    } catch (error) {
      dispatchMessage(dispatch, "error", "Invalid JSON format");
    }
  };
  const validateCode = (mode, editorValue) => {
    if (mode === "python") {
      return validatePythonIndentation(editorValue);
    }
    return [];
  };

  const handleValidationErrors = (mode, errors, dispatch) => {
    const criticalErrors = errors.filter((error) => error.severity === 8);
    if (criticalErrors.length > 0) {
      const language = mode === "yaml" ? "YAML " : "";
      dispatchMessage(
        dispatch,
        "error",
        `Please fix ${language}indentation errors before saving. Check lines: ${criticalErrors.map((e) => e.line).join(", ")}`
      );
      return true;
    }
    return false;
  };

  const performValidation = (mode, editorValue, dispatch) => {
    const errors = validateCode(mode, editorValue);
    return handleValidationErrors(mode, errors, dispatch);
  };

  const handleSave = () => {
    if (["python", "yaml"].includes(mode)) {
      if (performValidation(mode, editorValue, dispatch)) {
        return;
      }
    }
    dispatch(setHideMessageAction(true));
    setSaveState("saving");
    setDisable(true);
    const payload = {
      value: editorValue,
      mode,
    };
    updateCode({
      chatId: selectedChat?.chat_id,
      payload,
      onSuccess: (res) => {
        setDisable(false);
        if (res.success) {
          if (mode === "yaml") {
            dispatch(
              setIsYamlSaved({ chat_id: selectedChat?.chat_id, saved: true })
            );
          }
          setSaveState("success");
          setIsSaved(true);
          dispatchMessage(
            dispatch,
            "success",
            res.message || "Updated chat data"
          );
          if (mode === "yaml") {
            dispatch(setSidebarState(true));
            dispatch(setPreviewState(true));
            triggerPipelineHistory(dispatch, selectedChat?.chat_id);
          }
          triggerGetInfoAPI(dispatch, selectedChat?.chat_id);
        } else {
          setSaveState(false);
          setIsSaved(false);
          dispatchMessage(
            dispatch,
            "error",
            res.message || "Failed to update chat data"
          );
        }
      },
      onError: (err) => {
        setSaveState(false);
        setDisable(false);
        handleSessionExpiry(dispatch, err);
        dispatchMessage(
          dispatch,
          "error",
          err?.message || "Failed to update chat data"
        );
      },
    });
  };

  const handleRun = (dry_run) => {
    if (["python", "yaml"].includes(mode)) {
      if (performValidation(mode, editorValue, dispatch)) {
        return;
      }
    }
    setRunState("running");
    setDisable(true);
    runCode({
      payload: {
        mode,
        dry_run,
        chat_id: selectedChat?.chat_id,
        details: {
          value: editorValue,
        },
      },
      onSuccess: (res) => {
        setDisable(false);
        if (res.success) {
          setRunState("success");
          dispatch(setHideMessageAction(true));
          dispatchMessage(
            dispatch,
            "success",
            res.message || "Successfully ran Pipeline"
          );
        } else {
          dispatch(setHideMessageAction(true));
          setRunState(false);
          dispatchMessage(
            dispatch,
            "error",
            res.message || "Failed to execute"
          );
        }
      },
      onError: (err) => {
        dispatch(setHideMessageAction(true));
        setDisable(false);
        setRunState(false);
        handleSessionExpiry(dispatch, err);
        dispatchMessage(
          dispatch,
          "error",
          err?.message || "Failed to update chat data"
        );
      },
    });
  };

  const handleCancel = () => {
    dispatch(setHideMessageAction(false));
    onChildrenDrawerClose();
    if (isSaved) {
      dispatchMessage(
        dispatch,
        "success",
        mode === "yaml" ? "Job Mode: YAML" : "Job Mode: Python"
      );
      setIsSaved(false);
    }
  };

  const isSaveDisabled = () => {
    if (mode !== "yaml" || !editorValue || !editorSuggestions[mode])
      return true;
    const suggestions = editorSuggestions[mode];
    return !suggestions?.some((sug) => editorValue?.includes(sug?.label));
  };

  return (
    <>
      {contextHolder}
      {messageData && (
        <div style={{ marginTop: "-15px", marginBottom: "10px" }}>
          <CustomMessage
            type={messageData?.type}
            message={messageData?.message}
          />
        </div>
      )}
      <div className="custom-editor">
        {loading ? (
          <Skeleton active />
        ) : (
          <>
            <Editor
              id={mode + "editor"}
              height="95%"
              language={isJobConfig ? editorType : mode}
              onChange={(text) => {
                setRunState(false);
                setEditorValue(text);
              }}
              value={editorValue}
              onMount={handleMount}
              options={{
                fontSize: "10px",
                wordWrap,
                scrollBeyondLastLine: false,
                renderControlCharacters: true,
                automaticLayout: true,
                lineNumbers: "on",
                renderWhitespace: "all",
                wrappingIndent: "indent",
                tabSize: 4,
                insertSpaces: true,
                detectIndentation: true,
                formatOnPaste: true,
                formatOnType: true,
              }}
            />
            <Space
              direction="horizontal"
              align="end"
              style={{ margin: "10px 0" }}
              className="dFlex justifyBetween"
            >
              <Space>
                <Button
                  data-testid="cancel-button"
                  onClick={() => handleCancel()}
                >
                  Cancel
                </Button>
                {mode === "yaml" && (
                  <Button
                    onClick={() => handleRun(true)}
                    style={{
                      backgroundColor: "rgb(242, 142, 30)",
                      color: "#ffffff",
                    }}
                    disabled={disable}
                    loading={runState === "running"}
                    data-testid="run-button"
                  >
                    Run
                  </Button>
                )}
                {mode === "yaml" || mode === "python" ? (
                  <Space>
                    <Button
                      data-testid="save-button"
                      type="primary"
                      onClick={handleSave}
                      loading={saveState === "saving"}
                      disabled={mode === "yaml" && isSaveDisabled()}
                    >
                      Save
                    </Button>
                    <Tooltip
                      title={TOOLTIPS_INFO.editorInfoMessage}
                      overlayClassName="custom-tooltip"
                    >
                      <InfoCircleOutlined style={{ fontSize: "12px" }} />
                    </Tooltip>
                  </Space>
                ) : (
                  <Button
                    data-testid="save-button"
                    type="primary"
                    onClick={handleSaveJobTrigger}
                  >
                    Save
                  </Button>
                )}
              </Space>

              {mode === "python" && (
                <div style={{ position: "relative", alignSelf: "end" }}>
                  <Button
                    style={{ marginRight: "20px" }}
                    onClick={() => setShowSupportBot((prev) => !prev)}
                    type="primary"
                    className="dFlex justifyCenter alignCenter"
                    data-testid="show-support-box-button"
                    icon={
                      <div>
                        {showSupportBot ? (
                          <Tooltip title="Close">
                            <CloseOutlined style={{ display: "block" }} />
                          </Tooltip>
                        ) : (
                          <Tooltip title="ACE Assistant">
                            <img
                              src={`${imagePath}/favicon.svg`}
                              style={{ height: "23px", display: "block" }}
                              alt="logo"
                            />
                          </Tooltip>
                        )}
                      </div>
                    }
                  />
                  {showSupportBot && (
                    <SuppportBot
                      selectedChat={selectedChat}
                      setEditorValue={setEditorValue}
                      messages={messages}
                      setMessages={setMessages}
                    />
                  )}
                </div>
              )}
            </Space>
          </>
        )}
      </div>
    </>
  );
};
export default CustomEditor;