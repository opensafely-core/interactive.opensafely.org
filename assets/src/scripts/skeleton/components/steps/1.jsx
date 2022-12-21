import { Form, Formik } from "formik";
import { default as React, useState } from "react";
import { useWizard } from "react-use-wizard";
import * as Yup from "yup";
import codelists from "../../data/codelists.json";
import CodelistSelect from "../CodelistSelect";
import Button from "../Button";

function Step1({ useFormState, setUseFormState }) {
  const { nextStep } = useWizard();
  const [isSecondCodelistVisible, setIsSecondCodelistVisible] = useState(
    !!useFormState?.codelists?.[1]
  );

  const FormSchema = Yup.object().shape({
    codelistType1: Yup.string()
      .oneOf(["event", "medication"])
      .required("Choose a codelist type"),
    codelist1: Yup.object().shape({
      label: Yup.string().required(),
      organisation: Yup.string().required(),
      value: Yup.string().required(),
    }),
    codelistType2: isSecondCodelistVisible
      ? Yup.string().oneOf(["event", "medication"]).required("Required")
      : undefined,
    codelist2: isSecondCodelistVisible
      ? Yup.object().shape({
          label: Yup.string().required(),
          organisation: Yup.string().required(),
          value: Yup.string().required(),
        })
      : undefined,
  });

  return (
    <div>
      <Formik
        initialValues={{
          codelist1: useFormState?.codelists?.[0],
          codelistType1: useFormState?.codelists?.[0]?.type,
          codelist2: useFormState?.codelists?.[1],
          codelistType2: useFormState?.codelists?.[1]?.type,
        }}
        validationSchema={FormSchema}
        onSubmit={(values) => {
          setUseFormState({
            codelists: [
              {
                type: values.codelistType1,
                label: values.codelist1.label,
                value: values.codelist1.value,
                organisation: values.codelist1.organisation,
              },
              {
                type: values.codelistType2,
                label: values.codelist2.label,
                value: values.codelist2.value,
                organisation: values.codelist1.organisation,
              },
            ],
          });
          nextStep();
        }}
        validateOnMount
      >
        {({
          errors,
          isValid,
          setFieldValue,
          touched,
          validateField,
          validateForm,
          values,
        }) => {
          return (
            <Form>
              <CodelistSelect
                codelists={codelists}
                errors={errors}
                id={1}
                setFieldValue={setFieldValue}
                touched={touched}
                values={values}
              />
              <div className="my-8 flex flex-row gap-6">
                {!isSecondCodelistVisible ? (
                  <Button
                    variant="success"
                    type="button"
                    onClick={() => setIsSecondCodelistVisible(true)}
                  >
                    Add another codelist
                  </Button>
                ) : null}
              </div>
              {isSecondCodelistVisible ? (
                <CodelistSelect
                  codelists={codelists}
                  errors={errors}
                  setFieldValue={setFieldValue}
                  touched={touched}
                  values={values}
                  id={2}
                />
              ) : null}
              {isSecondCodelistVisible ? (
                <Button
                  variant="danger"
                  type="button"
                  onClick={() => {
                    setIsSecondCodelistVisible(false);
                    setFieldValue("codelist2", undefined);
                    setFieldValue("codelistType2", undefined);
                    validateForm();
                    validateField("codelist2");
                    validateField("codelistType2");
                  }}
                >
                  Remove this codelist
                </Button>
              ) : null}
              <div className="block my-3">
                <Button
                  disabled={!isValid}
                  variant="primary"
                  size="lg"
                  type="submit"
                >
                  Next
                </Button>
              </div>
              <div className="my-8 p-8 bg-blue-50 overflow-x-scroll">
                <pre>{JSON.stringify(values, null, 2)}</pre>
              </div>
            </Form>
          );
        }}
      </Formik>
    </div>
  );
}

export default Step1;
