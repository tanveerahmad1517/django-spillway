from rest_framework.filters import BaseFilterBackend

from spillway import forms
from spillway.query import filter_geometry


class GeoQuerySetFilter(BaseFilterBackend):
    """A Filter for calling GeoQuerySet methods."""
    precision = 4

    def filter_queryset(self, request, queryset, view):
        format = request.accepted_renderer.format
        try:
            has_format = queryset.has_format(format)
        except AttributeError:
            # Handle default GeoQuerySet.
            try:
                return getattr(queryset, format)(precision=self.precision)
            except AttributeError:
                return queryset
        params = view.clean_params()
        tolerance, srs = map(params.get, ('simplify', 'srs'))
        srid = getattr(srs, 'srid', None)
        kwargs = {}
        if has_format:
            kwargs.update(precision=self.precision, format=format)
        return queryset.simplify(tolerance, srid, **kwargs)


class SpatialLookupFilter(BaseFilterBackend):
    """A Filter providing backend supported spatial lookups like intersects,
    overlaps, etc.
    """

    def filter_queryset(self, request, queryset, view):
        form = forms.SpatialQueryForm(request.QUERY_PARAMS)
        params = form.cleaned_data if form.is_valid() else {}
        return filter_geometry(queryset, **params)
