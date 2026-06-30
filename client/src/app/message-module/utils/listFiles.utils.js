import { FileOutlined } from "@ant-design/icons";

export const getLoadedFiles = (files, selectedFiles) => {
  let fileNames = "";
  let loadedFiles = files.filter((file) => {
    if (selectedFiles.includes(file.source_id)) {
      fileNames += file.alias + " ";
      return true;
    }
    return false;
  });
  return { loadedFiles, fileNames };
};

export const generateListData = (files, isLastItem) => {
  return files.map((file) => {
    return {
      label: <span>{file.alias}</span>,
      key: file.source_id,
      icon: <FileOutlined />,
      title: file.alias,
      disabled: isLastItem ? false : true,
    };
  });
};

export const isLoadFileDisabled = (isLastItem, isDisabled) => {
  return !isLastItem ? true : isDisabled;
};

export const handleFileBlobDownload = ({
  blobData,
  contentType,
  fallbackExtension = "xlsx",
  fallbackFileName = "download",
  originalFileName,
  supportedTypes = ["xlsx", "csv", "pdf", "doc", "docx", "json"],
}) => {
  const typeMap = {
    csv: "csv",
    "text/csv": "csv",
    sheet: "xlsx",
    excel: "xlsx",
    xlsx: "xlsx",
    json: "json",
    "application/json": "json",
    "text/json": "json",
    pdf: "pdf",
    word: "docx",
    doc: "docx",
    docx: "docx",
  };
  const getExtension = () => {
    const match = Object.entries(typeMap).find(([key]) =>
      contentType?.toLowerCase().includes(key)
    );
    return match?.[1] || fallbackExtension;
  };
  const extension = getExtension();
  const fileName = (() => {
    if (originalFileName) {
      const originalExt = originalFileName.split(".").pop().toLowerCase();
      if (!supportedTypes.includes(originalExt)) {
        return originalFileName.includes(".")
          ? originalFileName.replace(/\.[^/.]+$/, `.${extension}`)
          : `${originalFileName}.${extension}`;
      }
      return originalFileName;
    }
    return `${fallbackFileName}.${extension}`;
  })();
  const blob = new Blob([blobData], {
    type: contentType || "application/octet-stream",
  });
  const url = window.URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), {
    href: url,
    download: fileName,
    style: "display: none",
  });
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    window.URL.revokeObjectURL(url);
    a.remove();
  }, 100);
};
