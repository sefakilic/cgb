import json


class UserInput:
    """Class definition for UserInput.

    UserInput class gives an interface to access the run parameters provided by
    the user. It allows us to make changes in the input format (currently,
    JSON) relatively easily. It also checks the content of the input and sets
    default values for parameters not specified by the user.

    The user specifies the parameters via two files:
    - the required input file which contains
      - the names and accession numbers for the analyzed genomes
      - the TF protein accession number and the collection of its binding sites
    - the optional configuration file that specifies other parameters.
    """
    def __init__(self, input_filename, config_filename=None):
        """Constructs Input object using the input file."""
        self._input = {}
        with open(input_filename) as f:
            for k, v in json.load(f).items():
                self._input[k] = v
        with open(config_filename) as f:
            self._input['config'] = {}
            for k, v in json.load(f).items():
                self._input['config'][k] = v

    @property
    def genome_name_and_accessions(self):
        """Returns the list of (genome name, accession_numbers) tuples."""
        return [(g['name'], g['accession_numbers'])
                for g in self._input['genomes']]

    @property
    def protein_accessions(self):
        """Returns the protein accession numbers."""
        return [p['protein_accession'] for p in self._input['motifs']]

    @property
    def TF_name(self):
        """Returns the TF of interest."""
        return self._input['TF']

    @property
    def sites_list(self):
        """Returns the lists of binding sites."""
        return [m['sites'] for m in self._input['motifs']]

    @property
    def log_dir(self):
        """Returns the directory to be used for logging."""
        directory = self._input['config']['log_dir']
        return directory

    @property
    def prior_regulation_probability(self):
        """Returns the prior probability of regulation.

        It is used by the Bayesian estimator of operon regulation as the prior
        probability of an operon being regulated.

        If not provided by the user, it is estimated by predicting operons in
        the genome of the TF for which the motif is provided and dividing the
        number of sites in the motif (assuming that there is one site per
        operon) by the number of operons. For instance, if 30 sites are
        available for LexA in E. coli, then the prior for regulation is
        30/~2300 operons. See "get_prior" in "main.py" for implementation.
        """
        try:
            value = self._input['config']['prior_regulation_probability']
        except KeyError:
            value = None
        return value

    @property
    def has_prior_probability_set(self):
        """Returns true if the prior probability of regulation is provided."""
        return 'prior_regulation_probability' in self._input['config']

    @property
    def probability_threshold(self):
        """Returns the threshold for regulation probabilities.

        Only the operons with a regulation probability above the threshold will
        be reported.

        The default value for the probability threshold is 0.5
        """
        try:
            value = self._input['config']['probability_threshold']
        except KeyError:
            value = 0.5
        return value

    @property
    def weighting_scheme(self):
        """Returns the option for motif combining.

        Options are
        - simple concatenation, "simple": Two collections will simply be
          combined. That is the more sites a motif has, the more its
          contribution to the final PSFM.
        - phylogenetic weighting, "phylogenetic". The weight of each motif will
          be determined by its phylogenetic distance to target species' TFs.

        The default value is 'simple'.
        """
        try:
            value = self._input['config']['weighting_scheme']
        except KeyError:
            value = 'simple'
        return value
