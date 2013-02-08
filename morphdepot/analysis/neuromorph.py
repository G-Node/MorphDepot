"""
This module deals with morphologies of single neurons. It is based on a data
representation by the `swc-specification <http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html>`_
"""
import numpy as np
import itertools

DATA_PATH = "data"
EXAMPLE_SWC_DATA = "example_morph.swc"


class Morph(object):
  """

  All examples have to be initialized with the following:

  >>> import numpy as np
  >>> from py_octopodba.neurosimlib.neuromorph import Morph
  >>> morph = Morph() # initialize with demo morphology
  """
  def __init__(self, swc_data=None):
    """
    This class is initialized with a swc-datastructure.
    """
    self.swc_data =  swc_data
    self.init_swc(swc_data)
    self.idx_entire_morph = np.ones(self.n_segments)

  def __repr__(self):
    return "<Morph> Number of segments: %s" % (sum(self.idx_entire_morph))

  def init_swc(self, swc_data=None):
    """
    This method

    * reads ``swc_data``, 
    * converts it into numpy arrays

      * ``self.seg_ids``
      * ``self.seg_xs``
      * ``self.seg_ys``
      * ``self.seg_zs``
      * ``self.seg_radii``
      * ``self.seg_prec_ids``

    * adds numpy arrays according to `preceding segments` (using
      :func:`add_preceding_segment_metricies`)

      * ``self.seg_prec_xs``
      * ``self.seg_prec_ys``
      * ``self.seg_prec_zs``
      * ``self.seg_prec_radii``

    * adds the attribute ``idx_vector`` as logical index with which the scope
      of analysis can be reduced to a subset of segments
    """
    if swc_data == None:
      import os
      this_dir, this_filename = os.path.split(__file__)
      example_swc_data = os.path.join(this_dir, DATA_PATH, EXAMPLE_SWC_DATA)
      self.swc_data = open(example_swc_data)
    data = np.loadtxt(self.swc_data)
    if len(data[1,:]) == 7:
      # Second column ``type`` of swc-specification is given, but will be
      # neglected
      type_shift = 1
    else:
      type_shift = 0
    self.seg_ids   = np.array(data[:,0], int)
    self.seg_xs    = np.array(data[:,1+type_shift], float)
    self.seg_ys    = np.array(data[:,2+type_shift], float)
    self.seg_zs    = np.array(data[:,3+type_shift], float)
    self.seg_radii = np.array(data[:,4+type_shift], float)
    self.seg_prec_ids = np.array(data[:,5+type_shift], int)
    self.n_segments = len(self.seg_ids)
    self.add_preceding_segment_metricies()
    self.reset_idx_vector()

  def reset_idx_vector(self):
    """
    This method resets ``idx_vector`` to point to all segments.
    """
    self.idx_vector = np.ones(self.n_segments, bool)
    return self.idx_vector

  def add_preceding_segment_metricies(self):
    """
    This method adds metric values of preceding segments to simplify analysis:

    * ``self.seg_prec_xs``
    * ``self.seg_prec_ys``
    * ``self.seg_prec_zs``
    * ``self.seg_prec_radii``

    .. Note:: The first segment has no preceding segment. Therefore, metric
       values of its *preceding segment* are a copy of the first element.
    """
    prec_xs = []
    prec_ys = []
    prec_zs = []
    prec_radii = []
    for idx in range(self.n_segments):
      if self.seg_prec_ids[idx] == -1:
        prec_xs.append(self.seg_xs[idx])
        prec_ys.append(self.seg_ys[idx])
        prec_zs.append(self.seg_zs[idx])
        prec_radii.append(self.seg_radii[idx])
      else:
        prec_xs.append(float(
            self.seg_xs[np.where(self.seg_ids == self.seg_prec_ids[idx])]))
        prec_ys.append(float(
            self.seg_ys[np.where(self.seg_ids == self.seg_prec_ids[idx])]))
        prec_zs.append(float(
            self.seg_zs[np.where(self.seg_ids == self.seg_prec_ids[idx])]))
        prec_radii.append(float(
            self.seg_radii[np.where(self.seg_ids == self.seg_prec_ids[idx])]))
    self.seg_prec_xs = np.array(prec_xs)
    self.seg_prec_ys = np.array(prec_ys)
    self.seg_prec_zs = np.array(prec_zs)
    self.seg_prec_radii = np.array(prec_radii)

  def get_seg_successors(self, seg_id):
    """
    Return value:
      a Boolean vector with ``True`` for successors of ``seg_id``.
    """
    return self.seg_prec_ids == seg_id

  def get_n_successors(self, idx_vector=None):
    """
    Return value:
      a numpy array with length of ``self.n_segments`` which gives the
      number of successors for the corresponding segment.
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    res_vector = np.zeros(self.n_segments)
    precs = [(g[0], len(list(g[1]))) for g in
        itertools.groupby(self.seg_prec_ids)]
    for prec in precs:
      res_vector[self.seg_ids==prec[0]] += prec[1]
    return res_vector * np.array(idx_vector, int)

  def get_branch_points(self, idx_vector=None):
    """
    Return value:
      numpy array as locigal index of branch points
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    n_successors = self.get_n_successors()
    return (n_successors[idx_vector]) > 1

  def get_n_branch_points(self, idx_vector=None):
    """
    Return value:
      number of branch points
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.get_branch_points(idx_vector))

  def get_subtree(self,sec):
    """
    Return value:
      numpy array as logical index pointing to segments that are part of the
      subtree of segment ``seg_id``

      If ``sec == -1`` the function returns an index pointing to all segments
      as it assumes that ``-1`` is the root compartment.

    Input parameter:
      ``seg_id`` (int): segment id of the first segment of the subtree

    Example:
      The subtree of segment 1 should contain the whole tree, therefore the sum
      of the returned index should be equal to the number of segments::

        from py_octopodba.neurosimlib.neuromorph import Morph
        morph = Morph() # initialize with demo morphology
        morph.n_segments == sum(morph.get_subtree(1))

    .. Note:: This method runs very slow! 
    """
    if sec == -1:
      return
    init_vector = np.zeros(self.n_segments, bool)
    init_vector[np.where(self.seg_ids==sec)[0]] = 1
    if sum(self.get_seg_successors(sec))==0:
      return init_vector
    else:
      subtree_vec = init_vector
      for sc in self.seg_ids[self.get_seg_successors(sec)==1]:
        subtree_vec += self.get_subtree(sc)
      return subtree_vec

  def get_terminal_tips(self, idx_vector=None):
    """
    Return value:
      numpy array as logical index pointing to segments that dont have any
      successor.
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    return (self.get_n_successors() == 0) * idx_vector 

  def get_length_of_segments(self, idx_vector=None):
    """
    Return value:
      numpy array with

      * length of indexed segments
      * 0 of non-indexed segments

    Example: as the example morphology was reconstructed with standard
    configuration of Felix Evers tracing module for Amira, segment length is
    always around 0.5 um. For our example analysis below we don't take the
    first segment into account as this is the root segment of the demo
    morphology (test this with ``morph.seg_prec_ids[0]`` which should give
    ``-1`` ). As the root segment has always length 0, below we don't use it for
    analysis.

    >>> len_vec = morph.get_length_of_segments()
    >>> len_vec = len_vec[1:] # cut out root segment
    >>> print np.mean(len_vec)
    0.499148712871
    >>> print np.max(len_vec)
    0.585906221165
    >>> print np.min(len_vec)
    0.295163039692
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    dxs = self.seg_xs - self.seg_prec_xs  
    dys = self.seg_ys - self.seg_prec_ys  
    dzs = self.seg_zs - self.seg_prec_zs  
    return np.sqrt(dxs**2 + dys**2 + dzs**2)*np.array(idx_vector, int)

  def get_surface_areas(self, idx_vector=None, with_tips=False):
    """
    .. highlight:: none
 
    Return value:
      numpy array with lateral surface_area [um^2] for each segment.  If
      with_tips=True the closing area of the terminal tips is added. This
      feature is by default False in order to correspond the NEURON output
      for::

        b = 0
        for a in neuron.h.allsec():
          b += neuron.h.area(0.5)
        print b

    .. highlight:: python
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    def lsa_frustum(r1, r2, h):
      """
      This function returns the lateral surface area of a frustum (here: a
      portion of a cone that lies between two parallel plains cutting the cone
      orthogonal to its longitudinal axis).
      """
      return (r1 + r2) * np.pi * np.sqrt(np.square(r1-r2) + np.square(h))
    lsa_vec_no_tips = lsa_frustum(self.seg_radii, self.seg_prec_radii,
        self.get_length_of_segments())
    if with_tips:
      #: tip surface areas (tsas)
      tsas = np.pi * self.seg_radii**2 * self.get_terminal_tips()
      lsa_vec = tsas + lsa_vec_no_tips # return area in cm^2
    else:
      lsa_vec = lsa_vec_no_tips # return area in cm^2
    return lsa_vec * np.array(idx_vector, int)

  def get_volumes(self, idx_vector=None):
    """
    Return value:
      numpy array with volume [um^3] for each segment.

    >>> sum(morph.get_volumes())
    4160.5125564764285
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    def vol_frustum(r1, r2, h):
      """
      This function returns the volume of a frustum (here: a portion
      of a cone that lies between two parallel plains cutting the cone
      orthogonal to its longitudinal axis).
      """
      return (h * np.pi) / 3 * (np.square(r1) + r1*r2 + np.square(r2))
    vol_vec = vol_frustum(self.seg_radii, self.seg_prec_radii,
        self.get_length_of_segments())
    return vol_vec * np.array(idx_vector, int)

  def get_total_length(self, idx_vector=None):
    """
    Return value:
      Length of (indicated/all) segments [numpy.float64]

    >>> print(morph.get_total_length())
    2448.82358534
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.get_length_of_segments()[idx_vector])

  def get_total_surface_area(self, idx_vector=None, with_tips=False):
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.get_surface_areas(idx_vector))

  def get_total_volume(self, idx_vector=None, with_tips=False):
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.get_volumes(idx_vector))
    
  def get_terminal_degrees(self, idx_vector=None):
    """
    Return value:
      numpy array with *terminal degree* for each segment.
      
    We defined the terminal degree of a given compartment as the sum of all
    terminal tips that finally emerge from it (Cuntz et al., 2007)

    For example, if a compartment led to three final branches, it was assigned
    a terminal degree of three. The terminal tip itself was assigned a terminal
    degree of one.

    Example:

    >>> print(morph.get_terminal_degrees())
    [140  59  81 ...,   1   1   1]
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    start_vec = np.array(self.get_terminal_tips(), int)
    for seg_id in np.where(start_vec==1)[0]:
      idx_current_seg_id = seg_id
      while True:
        current_seg_id = self.seg_prec_ids[idx_current_seg_id]
        idx_current_seg_id = np.where(self.seg_ids==current_seg_id)[0][0]
        start_vec[idx_current_seg_id] += 1
        if self.seg_prec_ids[idx_current_seg_id] == -1:
          break
    return start_vec * np.array(idx_vector, int)

  def get_n_terminal_tips(self, idx_vector=None):
    """
    Return value:
      Sum of terminal tips

    >>> print(morph.get_n_terminal_tips())
    140
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.get_terminal_tips()[idx_vector])

  def get_mean_terminal_length(self, idx_vector=None):
    """
    Return value:
     Mean length of terminals [um]

    >>> print(morph.get_mean_terminal_length())
    8.59972648964
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    tl_terminals = self.get_total_length(
        self.get_terminal_degrees(idx_vector)==1)
    n_terminals = self.get_n_terminal_tips(idx_vector)
    return tl_terminals / n_terminals

  def get_mean_seg_radius(self, idx_vector=None):
    """
    Return value:
     Mean radius of segments [um]

    >>> print(morph.get_mean_seg_radius())
    0.553663806807
    """
    if idx_vector == None:
      idx_vector = self.idx_vector
    return sum(self.seg_radii[idx_vector])/sum(idx_vector)

  def get_surface_volume_ratio(self,idx_vector=None):
    if idx_vector == None:
      idx_vector = self.idx_vector
    surface_area = self.get_total_surface_area(idx_vector)
    volume = self.get_total_volume(idx_vector)
    return  surface_area /volume
        
