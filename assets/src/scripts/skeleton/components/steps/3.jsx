import React from "react";
import { useWizard } from "react-use-wizard";

function Step3() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      {/* Filters */}
      <button onClick={() => previousStep()} type="button">
        Previous ⏮️
      </button>
      <button onClick={() => nextStep()} type="button">
        Submit
      </button>
    </>
  );
}

export default Step3;
