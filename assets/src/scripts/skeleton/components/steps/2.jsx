import React from "react";
import { useWizard } from "react-use-wizard";

function Step2() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      {/* Report builder */}
      <button type="button" onClick={() => previousStep()}>
        Previous ⏮️
      </button>
      <button type="button" onClick={() => nextStep()}>
        Next ⏭
      </button>
    </>
  );
}

export default Step2;
