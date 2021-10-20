from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator
from rest_framework import serializers

from .models import Stadium, StadiumSeats


class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = '__all__'


class StadiumSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumSeats
        fields = '__all__'


class SeatsGroupSerializer(serializers.Serializer):
    x_range = serializers.ListField(validators=[MaxLengthValidator(2), MinLengthValidator(2)])
    y_range = serializers.ListField(validators=[MaxLengthValidator(2), MinLengthValidator(2)])
    x_angle = serializers.FloatField(validators=[MinValueValidator(0)])
    y_angle = serializers.FloatField(validators=[MinValueValidator(0)])
    starting_row = serializers.IntegerField(validators=[MinValueValidator(1)])
    starting_column = serializers.IntegerField(validators=[MinValueValidator(1)])
    ending_column = serializers.IntegerField(validators=[MinValueValidator(1)])
    starting_number = serializers.IntegerField(validators=[MinValueValidator(1)])
    stadium = serializers.PrimaryKeyRelatedField(queryset=Stadium.objects.all())

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def validate(self, attrs):
        if attrs.get('starting_column') > attrs.get('ending_column'):
            raise serializers.ValidationError(
                {'starting_column': 'Starting Column cannot be greater than ending column'})
        return attrs

    @staticmethod
    def create_instance(**kwargs):
        return StadiumSeats(**kwargs)

    def create(self, validated_data):
        x_range = validated_data['x_range']
        y_range = validated_data['y_range']
        x_angle = validated_data['x_angle']
        y_angle = validated_data['y_angle']
        starting_row = validated_data['starting_row']
        starting_column = validated_data['starting_column']
        ending_column = validated_data['ending_column'] + 1
        starting_number = validated_data['starting_number']
        stadium = validated_data['stadium']

        x_min = min(x_range[0], x_range[1])
        x_max = max(x_range[0], x_range[1])
        y_min = min(y_range[0], y_range[1])
        y_max = max(y_range[0], y_range[1])
        y_ratio = (y_max - y_min) / y_angle
        if (ending_column - starting_column) != y_ratio:
            raise serializers.ValidationError({'y_angle': 'amount is greater/less than columns size'})
        final_data = list()
        current_row = starting_row
        current_col = starting_column
        seat_no = starting_number
        current_y = y_min
        last_y = y_min
        coord_x = x_min
        while coord_x < x_max:
            for column in range(starting_column, ending_column):
                instance = SeatsGroupSerializer.create_instance(
                    x_coordinate=coord_x,
                    y_coordinate=current_y,
                    seat_no=seat_no,
                    row=current_row,
                    column=column,
                    stadium=stadium
                )
                final_data.append(instance)
                current_y += y_angle if abs(y_min) < abs(y_max) else -1 * y_angle
                current_col += 1
            current_row += 1
            seat_no += 1
            if coord_x <= 0:
                last_y = last_y + y_angle if abs(y_min) < abs(y_max) else -1 * y_angle
            else:
                last_y = last_y - y_angle if abs(y_min) < abs(y_max) else -1 * y_angle
            current_y = last_y
            coord_x += x_angle
        return StadiumSeats.objects.bulk_create(final_data)


class SeatsColumnOnlySerializer(serializers.Serializer):
    x_coordinate = serializers.FloatField()
    y_coordinate = serializers.FloatField()
    y_angle = serializers.FloatField(validators=[MinValueValidator(0)])
    row = serializers.IntegerField(validators=[MinValueValidator(1)])
    starting_column = serializers.IntegerField(validators=[MinValueValidator(1)])
    ending_column = serializers.IntegerField(validators=[MinValueValidator(1)])
    seat_no = serializers.IntegerField(validators=[MinValueValidator(1)])
    stadium = serializers.PrimaryKeyRelatedField(queryset=Stadium.objects.all())

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        if attrs.get('starting_column', 1) > attrs.get('ending_column', 0):
            raise serializers.ValidationError(
                {'starting_column': 'Starting Column cannot be greater than ending column'})
        return attrs

    def create(self, validated_data):
        x_coordinate = validated_data['x_coordinate']
        y_coordinate = validated_data['y_coordinate']
        y_angle = validated_data['y_angle']
        row = validated_data['row']
        starting_column = validated_data['starting_column']
        ending_column = validated_data['ending_column'] + 1
        seat_no = validated_data['seat_no']
        stadium = validated_data['stadium']

        final_data = list()
        for col in range(starting_column, ending_column):
            instance = SeatsGroupSerializer.create_instance(
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                seat_no=seat_no,
                row=row,
                column=col,
                stadium=stadium
            )
            final_data.append(instance)
            y_coordinate += y_angle
        return StadiumSeats.objects.bulk_create(final_data)


class SeatsRowOnlySerializer(serializers.Serializer):
    x_coordinate = serializers.FloatField()
    y_coordinate = serializers.FloatField()
    x_angle = serializers.FloatField(validators=[MinValueValidator(0)])
    y_angle = serializers.FloatField(validators=[MinValueValidator(0)])
    starting_row = serializers.IntegerField(validators=[MinValueValidator(1)])
    ending_row = serializers.IntegerField(validators=[MinValueValidator(1)])
    column = serializers.IntegerField(validators=[MinValueValidator(1)])
    starting_number = serializers.IntegerField(validators=[MinValueValidator(1)])
    stadium = serializers.PrimaryKeyRelatedField(queryset=Stadium.objects.all())

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        if attrs.get('starting_row', 1) > attrs.get('ending_row', 0):
            raise serializers.ValidationError(
                {'starting_row': 'Starting row cannot be greater than ending row'})
        return attrs

    def create(self, validated_data):
        x_coordinate = validated_data['x_coordinate']
        y_coordinate = validated_data['y_coordinate']
        x_angle = validated_data['x_angle']
        y_angle = validated_data['y_angle']
        starting_row = validated_data['starting_row']
        ending_row = validated_data['ending_row'] + 1
        column = validated_data['column']
        starting_number = validated_data['starting_number']
        stadium = validated_data['stadium']

        final_data = list()

        for row in range(starting_row, ending_row):
            instance = SeatsGroupSerializer.create_instance(
                x_coordinate=x_coordinate,
                y_coordinate=y_coordinate,
                seat_no=starting_number,
                row=row,
                column=column,
                stadium=stadium
            )
            final_data.append(instance)
            x_coordinate += x_angle
            if x_coordinate > 0:
                y_coordinate -= y_angle
            else:
                y_coordinate += y_angle
            starting_number += 1
        return StadiumSeats.objects.bulk_create(final_data)
