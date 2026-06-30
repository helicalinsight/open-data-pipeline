import React from 'react';
import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DetailedView from '../../../app/audit-module/detailedView';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import * as auditService from '../../../apis/auditService';
import dayjs from 'dayjs';
const mockStore = configureStore([]);

beforeAll(() => {
  window.matchMedia = window.matchMedia || function () {
    return {
      matches: false,
      addListener: jest.fn(),
      removeListener: jest.fn(),
    };
  };
});
const None = null;
describe('DetailedView Component', () => {
  let store;
  let onBackMock;

  beforeEach(() => {
    onBackMock = jest.fn();
    store = mockStore({
      audit: {
        detailData: {
          Audits: [
            { Chat_id: 'C1', Run_id: 'R1', Schedule_id: 'S1', Total_run_cost: 100, mode: 'pipeline' },
            { Chat_id: 'C2', Run_id: 'R2', Schedule_id: 'S2', Total_run_cost: 200, mode: 'code' },
          ],
        },
        dateRange: {
          startTime: '2024-03-04',
          endTime: '2024-07-09',
        },
      },
    });

    jest.clearAllMocks();
  });
  const renderComponent = () =>
    render(
      <Provider store={store}>
        <DetailedView onBack={onBackMock} />
      </Provider>
    );


  it('renders correct number of data rows', async () => {
    renderComponent();
    const rows = await screen.findAllByRole('row');
    expect(rows.length).toBeGreaterThanOrEqual(2);
  });

  it('fetches detail data when date range is changed', async () => {
    renderComponent();

    const startDate = dayjs('2024-03-10');
    const endDate = dayjs('2024-03-20');
    const mockData = {
      Audits: [
        { Chat_id: 'C3', Run_id: 'R3', Schedule_id: 'S3', Total_run_cost: 150, mode: 'code' },
      ],
    };

    jest.spyOn(auditService, 'getDetailData').mockImplementation(({ onSuccess }) => {
      onSuccess(mockData);
    });

    const datePicker = screen.getByPlaceholderText('Start date');
    fireEvent.click(datePicker);
    fireEvent.change(screen.getByPlaceholderText('Start date'), { target: { value: startDate.format('YYYY-MM-DD') } });
    fireEvent.change(screen.getByPlaceholderText('End date'), { target: { value: endDate.format('YYYY-MM-DD') } });
    fireEvent.keyDown(screen.getByPlaceholderText('End date'), { key: 'Enter' });
  });

  it('handles error during fetching detail data', async () => {
    renderComponent();

    const startDate = dayjs('2024-03-10');
    const endDate = dayjs('2024-03-20');

    jest.spyOn(auditService, 'getDetailData').mockImplementation(({ onError }) => {
      onError({ message: 'Error fetching data' });
    });

    const datePicker = screen.getByPlaceholderText('Start date');
    fireEvent.click(datePicker);
    fireEvent.change(screen.getByPlaceholderText('Start date'), { target: { value: startDate.format('YYYY-MM-DD') } });
    fireEvent.change(screen.getByPlaceholderText('End date'), { target: { value: endDate.format('YYYY-MM-DD') } });
    fireEvent.keyDown(screen.getByPlaceholderText('End date'), { key: 'Enter' });
  });
  it('displays default values for Schedule_id and Run_id when they are missing', async () => {
    store = mockStore({
      audit: {
        detailData: {
          Audits: [
            { Chat_id: 'C1', Run_id: null, Schedule_id: 'S1', Total_run_cost: 100, mode: 'code' },
            { Chat_id: 'C2', Run_id: 'R2', Schedule_id: null, Total_run_cost: 200, mode: 'pipeline' },
          ],
        },
        dateRange: {
          startTime: '2024-03-04',
          endTime: '2024-07-09',
        },
      },
    });
    renderComponent();
    const rows = await screen.findAllByRole('row');
    expect(rows.length).toBeGreaterThanOrEqual(2);
    const rowWithDash = rows.find(row => row.textContent.includes('-'));
    expect(rowWithDash).toBeInTheDocument();
  });
  it('displays default values for Schedule_id and Run_id when they are None', async () => {
    store = mockStore({
      audit: {
        detailData: {
          Audits: [
            { Chat_id: 'C1', Run_id: null, Schedule_id: 'S1', Total_run_cost: 100, mode: 'code' },
            { Chat_id: 'C2', Run_id: 'R2', Schedule_id: null, Total_run_cost: 200, mode: 'pipeline' },
          ],
        },
        dateRange: {
          startTime: '2024-03-04',
          endTime: '2024-07-09',
        },
      },
    });
    renderComponent();
    const rows = await screen.findAllByRole('row');
    expect(rows.length).toBeGreaterThanOrEqual(2);
    const cells = rows.flatMap(row => within(row).queryAllByRole('cell'));
    const cellWithDash = cells.find(cell => cell.textContent.includes('-'));
    expect(cellWithDash).toBeInTheDocument();
  });
});
