import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import LogViewerDrawer from '../../../../app/job-schedule-module/components/LogViewerDrawer';

jest.mock('@patternfly/react-log-viewer', () => ({
  LogViewer: jest.fn((props) => (
    <div data-testid="mock-log-viewer" {...props}>Mock LogViewer</div>
  )),
  LogViewerSearch: jest.fn(() => (
    <input data-testid="mock-log-viewer-search" placeholder="Search" />
  )),
}));

jest.mock('antd', () => ({
  ...jest.requireActual('antd'),
  message: {
    success: jest.fn(),
    error: jest.fn(),
    open: jest.fn(),
  },
}));

const mockStore = configureStore([]);

describe('LogViewerDrawer Component', () => {
  let store;
  let defaultProps;

  beforeEach(() => {
    store = mockStore({
      jobSchedule: {
        logValue: 'Sample log content',
        logDetails: {
          schedule_id: '123',
          run_id: 'abc',
          local: true,
        },
      },
      chat: {
        selectedChat: {
          chat_name: 'TestChat',
        },
      },
    });

    defaultProps = {
      loading: false,
      logs: 'Sample log content',
      isTextWrapped: false,
      setIsTextWrapped: jest.fn(),
      isFullScreen: false,
      setIsFullScreen: jest.fn(),
      logViewerRef: { current: { scrollToTop: jest.fn(), scrollToBottom: jest.fn() } },
      setOpenJobModal: jest.fn(),
      modalOpen: true,
      setModalOpen: jest.fn(),
      individualJob: false,
    };
  });

  describe('Initial Render', () => {
    it('should render the drawer with log content', () => {
      render(
        <Provider store={store}>
          <LogViewerDrawer {...defaultProps} />
        </Provider>
      );
    });

    it('should call scrollToBottom when logValue exists', () => {
      render(
        <Provider store={store}>
          <LogViewerDrawer {...defaultProps} />
        </Provider>
      );
      expect(defaultProps.logViewerRef.current.scrollToBottom).toHaveBeenCalled();
    });

    it('should not call scrollToBottom when logValue is empty', () => {
      const emptyLogStore = mockStore({
        jobSchedule: {
          logValue: '',
          logDetails: {
            schedule_id: '123',
            run_id: 'abc',
            local: true,
          },
        },
        chat: {
          selectedChat: {
            chat_name: 'TestChat',
          },
        },
      });
      render(
        <Provider store={emptyLogStore}>
          <LogViewerDrawer {...defaultProps} />
        </Provider>
      );
      expect(defaultProps.logViewerRef.current.scrollToBottom).not.toHaveBeenCalled();
    });
  });

  describe('Download Button', () => {
    it('should not show Download button if log does not include SUCCESS', () => {
      const newStore = mockStore({
        jobSchedule: {
          logValue: 'Some failure log',
          logDetails: { schedule_id: '123', run_id: 'abc', local: true },
        },
        chat: {
          selectedChat: { chat_name: 'TestChat' },
        },
      });
      render(
        <Provider store={newStore}>
          <LogViewerDrawer {...defaultProps} />
        </Provider>
      );
      expect(screen.queryByTestId('download_logs_id')).toBeNull();
    });

    it('should show Download button if log includes SUCCESS', () => {
      const successStore = mockStore({
        jobSchedule: {
          logValue: 'SUCCESS: Job completed',
          logDetails: { schedule_id: '123', run_id: 'abc', local: true },
        },
        chat: {
          selectedChat: { chat_name: 'TestChat' },
        },
      });
      render(
        <Provider store={successStore}>
          <LogViewerDrawer {...defaultProps} />
        </Provider>
      );
    });
  });
});