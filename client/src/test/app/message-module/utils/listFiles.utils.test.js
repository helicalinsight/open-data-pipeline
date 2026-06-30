import { FileOutlined } from "@ant-design/icons";
import {
  generateListData,
  getLoadedFiles,
  isLoadFileDisabled,
  handleFileBlobDownload 
} from "../../../../app/message-module/utils/listFiles.utils";

const originalCreateElement = document.createElement;
const originalCreateObjectURL = window.URL.createObjectURL;
const originalRevokeObjectURL = window.URL.revokeObjectURL;
const originalAppendChild = document.body.appendChild;
const originalRemove = Element.prototype.remove;
const originalClick = HTMLElement.prototype.click;

describe("generateListData function", () => {
  const files = [
    { source_id: 1, alias: "File1" },
    { source_id: 2, alias: "File2" },
  ];

  it("generates list data with correct properties when isLastItem is true", () => {
    const isLastItem = true;
    const listData = generateListData(files, isLastItem);

    listData.forEach((item, index) => {
      expect(item.label).toEqual(<span>{files[index].alias}</span>);
      expect(item.key).toEqual(files[index].source_id);
      expect(item.icon).toEqual(<FileOutlined />);
      expect(item.title).toEqual(files[index].alias);
      expect(item.disabled).toEqual(false);
    });
  });

  it("generates list data with correct properties when isLastItem is false", () => {
    const isLastItem = false;
    const listData = generateListData(files, isLastItem);

    listData.forEach((item, index) => {
      expect(item.label).toEqual(<span>{files[index].alias}</span>);
      expect(item.key).toEqual(files[index].source_id);
      expect(item.icon).toEqual(<FileOutlined />);
      expect(item.title).toEqual(files[index].alias);
      expect(item.disabled).toEqual(true);
    });
  });

  it("generates an empty list when files array is empty", () => {
    const isLastItem = true;
    const emptyFiles = [];
    const listData = generateListData(emptyFiles, isLastItem);

    expect(listData).toHaveLength(0);
  });
});

describe("getLoadedFiles function", () => {
  const files = [
    { source_id: 1, alias: "File1" },
    { source_id: 2, alias: "File2" },
    { source_id: 3, alias: "File3" },
  ];

  it("returns loaded files and file names when some files are selected", () => {
    const selectedFiles = [1, 3];
    const result = getLoadedFiles(files, selectedFiles);

    expect(result.loadedFiles).toEqual([
      { source_id: 1, alias: "File1" },
      { source_id: 3, alias: "File3" },
    ]);
    expect(result.fileNames).toEqual("File1 File3 ");
  });

  it("returns empty loaded files and file names when no files are selected", () => {
    const selectedFiles = [];
    const result = getLoadedFiles(files, selectedFiles);

    expect(result.loadedFiles).toEqual([]);
    expect(result.fileNames).toEqual("");
  });

  it("returns empty loaded files and file names when selected files are not in the list", () => {
    const selectedFiles = [4, 5];
    const result = getLoadedFiles(files, selectedFiles);

    expect(result.loadedFiles).toEqual([]);
    expect(result.fileNames).toEqual("");
  });

  it("returns empty loaded files and file names when files array is empty", () => {
    const selectedFiles = [1, 2];
    const emptyFiles = [];
    const result = getLoadedFiles(emptyFiles, selectedFiles);

    expect(result.loadedFiles).toEqual([]);
    expect(result.fileNames).toEqual("");
  });
});

describe("isLoadFileDisabled function", () => {
  it("returns true when isLastItem is false", () => {
    const result = isLoadFileDisabled(false, true);
    expect(result).toBe(true);
  });

  it("returns true when isLastItem is true and isDisabled is true", () => {
    const result = isLoadFileDisabled(true, true);
    expect(result).toBe(true);
  });

  it("returns false when isLastItem is true and isDisabled is false", () => {
    const result = isLoadFileDisabled(true, false);
    expect(result).toBe(false);
  });

  it("returns true when isLastItem is false and isDisabled is true", () => {
    const result = isLoadFileDisabled(false, true);
    expect(result).toBe(true);
  });

  it("returns true when both isLastItem and isDisabled are false", () => {
    const result = isLoadFileDisabled(false, false);
    expect(result).toBe(true);
  });

  it("returns false when both isLastItem and isDisabled are true", () => {
    const result = isLoadFileDisabled(true, false);
    expect(result).toBe(false);
  });
});

beforeEach(() => {
  document.createElement = jest.fn().mockImplementation((tagName) => {
    const element = {
      tagName: tagName.toUpperCase(),
      style: {},
      href: '',
      download: '',
      click: jest.fn(),
      remove: jest.fn()
    };
    return element;
  });
  window.URL.createObjectURL = jest.fn().mockReturnValue('blob:test-url');
  window.URL.revokeObjectURL = jest.fn();
  document.body.appendChild = jest.fn();
  Element.prototype.remove = jest.fn();
  HTMLElement.prototype.click = jest.fn();
  jest.useFakeTimers();
});

afterEach(() => {
  document.createElement = originalCreateElement;
  window.URL.createObjectURL = originalCreateObjectURL;
  window.URL.revokeObjectURL = originalRevokeObjectURL;
  document.body.appendChild = originalAppendChild;
  Element.prototype.remove = originalRemove;
  HTMLElement.prototype.click = originalClick;
  jest.useRealTimers();
  jest.clearAllMocks();
});

describe("handleFileBlobDownload function", () => {
  const mockBlobData = new ArrayBuffer(10);
  it("downloads file with correct extension from content type", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      originalFileName: "test"
    });
    expect(document.createElement).toHaveBeenCalledWith('a');
    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(document.body.appendChild).toHaveBeenCalled();
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('test.xlsx');
    expect(anchorElement.href).toBe('blob:test-url');
    jest.advanceTimersByTime(100);
    expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url');
    expect(anchorElement.remove).toHaveBeenCalled();
  });

  it("uses fallback extension when content type is not recognized", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "unknown/type",
      fallbackExtension: "txt",
      originalFileName: "test"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('test.txt');
  });

  it("uses fallback filename when no originalFileName is provided", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/json"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('download.json');
  });

  it("replaces unsupported file extension with supported one", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/json",
      originalFileName: "data.txt" 
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('data.json');
  });

  it("adds extension when original filename has no extension", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/pdf",
      originalFileName: "document"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('document.pdf');
  });

  it("preserves original extension when it's supported", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/pdf",
      originalFileName: "document.pdf"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('document.pdf');
  });

  it("handles CSV content type correctly", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "text/csv",
      originalFileName: "data"
    })
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('data.csv');
  });

  it("handles JSON content type correctly", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/json",
      originalFileName: "config"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('config.json');
  });

  it("handles Word document content type correctly", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      originalFileName: "report"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('report.docx');
  });

  it("uses octet-stream when no content type is provided", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      originalFileName: "file"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('file.xlsx');
  });

  it("cleans up URL and removes anchor element after timeout", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/pdf",
      originalFileName: "test.pdf"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(window.URL.revokeObjectURL).not.toHaveBeenCalled();
    expect(anchorElement.remove).not.toHaveBeenCalled();
    // After timeoutt
    jest.advanceTimersByTime(100);
    expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:test-url');
    expect(anchorElement.remove).toHaveBeenCalled();
  });

  it("handles complex filename with multiple dots correctly", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "application/json",
      originalFileName: "my.data.file.txt" 
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('my.data.file.json');
  });

  it("uses custom fallback values when provided", () => {
    handleFileBlobDownload({
      blobData: mockBlobData,
      contentType: "unknown/type",
      fallbackExtension: "bin",
      fallbackFileName: "backup",
      originalFileName: "invalid.unsupported"
    });
    const anchorElement = document.createElement.mock.results[0].value;
    expect(anchorElement.download).toBe('invalid.bin');
  });
});