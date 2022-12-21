import { Formik } from "formik";
import React, { useEffect, useState } from "react";
import { Wizard } from "react-use-wizard";
import * as Yup from "yup";
import Debug from "./components/Debug";
import { Step2, Step3 } from "./components/steps";
import Step1X from "./components/steps/1x";
import codelists from "./data/codelists.json";

function App() {
  const codelistTypes = codelists.map((a) => a.id);
  const [codelistCount, useCodelistCount] = useState(1);
  const [codelistValues, useCodelistValues] = useState({});

  const FormSchema = Yup.object().shape({
    codelistType: Yup.string()
      .oneOf(codelistTypes)
      .required("Choose a codelist type"),
    codelist: Yup.string().required("Select a codelist"),
  });

  useEffect(() => {
    useCodelistValues(
      Array(codelistCount)
        .fill(0)
        .map((i) => ({ [`codelistType${i}`]: "", [`codelist${i}`]: "" }))
    );
  }, [codelistCount]);

  return (
    <>
      <Formik
        initialValues={{
          ...codelistValues,
        }}
        validationSchema={FormSchema}
        validateOnMount
      >
        <>
          <Wizard>
            <Step1X
              codelistCount={codelistCount}
              useCodelistCount={useCodelistCount}
            />
            <Step2 />
            <Step3 />
          </Wizard>
          <Debug />
        </>
      </Formik>
    </>
  );
}

export default App;
