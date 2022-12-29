import { useFormikContext } from "formik";
import React from "react";
import { useWizard } from "react-use-wizard";
import Button from "../Button";
import Checkbox from "../Checkbox";
import InputFeedback from "../InputFeedback";
import RadioButton from "../RadioButton";

function Step4() {
  const { previousStep, nextStep } = useWizard();
  const { errors, touched } = useFormikContext();

  return (
    <>
      <h1 className="text-4xl font-bold mb-4">Set report filters</h1>
      <fieldset className="mt-12">
        <legend className="text-2xl font-bold mb-4">
          <h2>Filter the population</h2>
        </legend>
        <div className="flex flex-col gap-4">
          <RadioButton
            id="all"
            label="All people"
            name="filterPopulation"
            value="all"
          />
          <RadioButton
            id="adults"
            label="Adults only"
            name="filterPopulation"
            value="adults"
          />
          <RadioButton
            id="children"
            label="Children only"
            name="filterPopulation"
            value="children"
          />
          {touched.filterPopulation && errors.filterPopulation ? (
            <InputFeedback error={errors.filterPopulation} />
          ) : null}
        </div>
      </fieldset>

      <fieldset className="mt-12">
        <legend className="text-2xl font-bold mb-4">
          <h2>Break down the report by demographics</h2>
        </legend>
        <div className="flex flex-col gap-4">
          <Checkbox id="sex" label="Sex" name="demographics" value="sex" />
          <Checkbox id="age" label="Age" name="demographics" value="age" />
          <Checkbox
            id="ethnicity"
            label="Ethnicity"
            name="demographics"
            value="ethnicity"
          />
          <Checkbox
            id="imd"
            label="Index of Multiple Deprivation (IMD)"
            name="demographics"
            value="imd"
          />
          <Checkbox
            id="region"
            label="Region"
            name="demographics"
            value="region"
          />
          {touched.demographics && errors.demographics ? (
            <InputFeedback error={errors.demographics} />
          ) : null}
        </div>
      </fieldset>
      <div className="flex flex-row w-full gap-2 mt-10">
        <Button onClick={() => nextStep()}>Next</Button>
        <Button onClick={() => previousStep()} variant="danger">
          Go back
        </Button>
      </div>
    </>
  );
}

export default Step4;
