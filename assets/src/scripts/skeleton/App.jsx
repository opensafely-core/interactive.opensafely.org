import { Field, Form, Formik } from "formik";
import React, { Fragment, useState } from "react";
import { useWizard, Wizard } from "react-use-wizard";
import * as Yup from "yup";
import Combobox from "./components/Combobox";
import RadioButton from "./components/RadioButton";
import RadioButtonGroup from "./components/RadioButtonGroup";
import useFormData from "./stores/form-data";
import codelists from "./data/codelists.json";

const props = {
  data: {
    choices: "react-dropdown-options",
    errors: "react-dropdown-errors",
    hint: "Codelists are published by OpenSAFELY on OpenCodelists and use the SNOMED CT coding system",
    id: "codelist_slug",
    label: "Search for a codelist",
    name: "codelist_slug",
  },
  errors: [],
};

function Step1() {
  const formData = useFormData((state) => state.formData);
  const { addFormData } = useFormData();
  const { nextStep } = useWizard();
  const FormSchema = Yup.object().shape({
    codelistType: Yup.string()
      .oneOf(["event", "medication"])
      .required("Required"),
    codelist: Yup.object().shape({
      label: Yup.string().required(),
      organisation: Yup.string().required(),
      value: Yup.string().required(),
    }),
  });

  return (
    <div>
      <h2>Select a codelist</h2>
      <Formik
        initialValues={{
          codelistType: formData?.codelistType,
          codelist: formData?.codelist,
        }}
        validationSchema={FormSchema}
        onSubmit={(values, actions) => {
          addFormData(values);
          nextStep();
        }}
      >
        {({ errors, touched, values, setFieldValue }) => {
          return (
            <Form>
              <RadioButtonGroup
                id="codelistTypes"
                label="Select a codelist type"
                value={values.radioGroup}
                error={errors.radioGroup}
                touched={touched.radioGroup}
                hideLabel
              >
                {codelists.map((type) => (
                  <Field
                    component={RadioButton}
                    key={type.id}
                    name="codelistType"
                    id={type.name.toLowerCase()}
                    label={type.name}
                    resetOnChange={() => setFieldValue("codelist", {})}
                  />
                ))}
              </RadioButtonGroup>
              {codelists.map((type) => (
                <Fragment key={type.id}>
                  {values?.codelistType === type.name.toLowerCase() ? (
                    <Combobox
                      choices={type.codelists}
                      label={type.id}
                      name="codelist"
                      setFieldValue={setFieldValue}
                      {...(values.codelist?.label && {
                        initialSelectedItem: values.codelist,
                      })}
                    />
                  ) : null}
                </Fragment>
              ))}
              <button type="submit">Submit</button>
              <div className="my-8 p-8 bg-blue-50">
                <pre>{JSON.stringify(values, null, 2)}</pre>
              </div>
            </Form>
          );
        }}
      </Formik>
    </div>
  );
}

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

function Step3() {
  const { previousStep, nextStep } = useWizard();

  return (
    <>
      {/* Filters */}
      <button type="button" onClick={() => previousStep()}>
        Previous ⏮️
      </button>
      <button type="button" onClick={() => nextStep()}>
        Next ⏭
      </button>
    </>
  );
}

function App() {
  const formData = useFormData((state) => state);

  return (
    <>
      <Wizard>
        <Step1 />
        <Step2 />
        <Step3 />
      </Wizard>
      <div className="my-8 p-8 bg-red-50">
        <pre>{JSON.stringify(formData, null, 2)}</pre>
      </div>
    </>
  );
}

export default App;
