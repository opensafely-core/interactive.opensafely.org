import React, { useState } from "react";
import { Wizard } from "react-use-wizard";
import { Step1, Step2, Step3 } from "./components/steps";

function App() {
  const [useFormState, setUseFormState] = useState({});

  return (
    <>
      <Wizard>
        <Step1 useFormState={useFormState} setUseFormState={setUseFormState} />
        <Step2 useFormState={useFormState} setUseFormState={setUseFormState} />
        <Step3 useFormState={useFormState} setUseFormState={setUseFormState} />
      </Wizard>
      <div className="my-8 p-8 bg-yellow-50 overflow-x-scroll">
        <pre>{JSON.stringify(useFormState, null, 2)}</pre>
      </div>
    </>
  );
}

export default App;
