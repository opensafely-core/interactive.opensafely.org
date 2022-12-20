import React from "react";
import { useWizard } from "react-use-wizard";

function Step3() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      {/* Filters */}
      <button type="button" onClick={() => previousStep()}>
        Previous ⏮️
      </button>
      <button type="button" onClick={() => nextStep()}>
        Submit
      </button>
    </>
  );
}

export default Step3;
