import React from "react";
import { render, screen, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import ADLoader from "../../components/ADLoader";
import BeatLoader from "../../components/ADLoader/BeatLoader/BeatLoader";

const BeatLoaderProps = {
  color: "#096DD9",
  size: 7,
};

// Fake timers using Jest

describe("ADLoader component", () => {
  //check if component is rendered
  it("should render the ADLoader component without errors", () => {
    render(<ADLoader />);
  });

  it("should renders the loader", () => {
    const { container } = render(<ADLoader />);
    expect(container.querySelector(".ad-loader")).toBeInTheDocument();
  });
});

describe("BeatLoader component", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.spyOn(global, 'setInterval')
  })

  afterEach(()=>{
    jest.clearAllTimers()
  })
  
  it("should render the Beat Loader component with no props without errors", () => {
    render(<BeatLoader/>);
  });

  it("should render the Beat Loader component with passed props without errors", () => {
    render(<BeatLoader {...BeatLoaderProps} />);
    expect(screen.getByTestId("beat-loader-id")).toBeInTheDocument();
  });

  it("should render loading dots", () => {
    render(<BeatLoader {...BeatLoaderProps} />);
    expect(screen.getAllByTestId("dots")).toHaveLength(3);
  });

  it("should change active dot with interval", ()=>{
    render(<BeatLoader {...BeatLoaderProps}/>)
    const dots = screen.getAllByTestId("dots");

    act(()=>{
      jest.advanceTimersByTime(170);
    })

    expect(dots[0]).toHaveClass("dot active")
    expect(dots[1]).not.toHaveClass("active")
    expect(dots[2]).not.toHaveClass("active")

    act(()=>{
      jest.advanceTimersByTime(170);
    })

    expect(dots[0]).not.toHaveClass("active")
    expect(dots[1]).toHaveClass("dot active")
    expect(dots[2]).not.toHaveClass("active")

    act(()=>{
      jest.advanceTimersByTime(170);
    })

    expect(dots[0]).not.toHaveClass("active")
    expect(dots[1]).not.toHaveClass("active")
    expect(dots[2]).toHaveClass("dot active")
  })
});