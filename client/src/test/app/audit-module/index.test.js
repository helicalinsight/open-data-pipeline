import React from 'react';
import { render, screen } from '@testing-library/react';
import AuditModule from '../../../app/audit-module';

const mockUseDispatch = jest.fn();
const mockUseSelector = jest.fn();

jest.mock('react-redux', () => ({
  useDispatch: () => mockUseDispatch,
  useSelector: (selector) => mockUseSelector(selector),
}));

jest.mock('../../../app/audit-module/summaryView', () => {
  return function MockSummaryView({ onBarClick }) {
    return <button onClick={onBarClick}>Click me to go to Detailed View</button>;
  };
});
jest.mock('../../../app/audit-module/detailedView', () => {
  return function MockDetailedView() {
    return <div>Detailed View</div>;
  };
});

describe('AuditModule', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders SummaryView initially when isDetailedView is false', () => {
    mockUseSelector.mockImplementation(selector => 
      selector({ audit: { isDetailedView: false } })
    );
    render(<AuditModule />);
  });

  it('renders DetailedView when isDetailedView is true', () => {
    mockUseSelector.mockImplementation(selector => 
      selector({ audit: { isDetailedView: true } })
    );
    render(<AuditModule />);
  });
});